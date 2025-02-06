import os
import subprocess
from flask import Flask, render_template, request
from gtts import gTTS
import openai

# Настройка API ключа GPT-4 (замените на свой ключ)
openai.api_key = os.getenv("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")
app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Главная страница с формой загрузки
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        photo = request.files["photo"]
        name = request.form["name"]

        if photo and name:
            # Сохранение фото
            photo_path = os.path.join(UPLOAD_FOLDER, photo.filename)
            photo.save(photo_path)

            # 1️⃣ Генерация исторического текста
            history_text = generate_history(name)

            # 2️⃣ Создание синтезированного голоса
            audio_path = os.path.join(OUTPUT_FOLDER, "voice.mp3")
            generate_voice(history_text, audio_path)

            # 3️⃣ Анимация лица
            output_video = os.path.join(OUTPUT_FOLDER, "animated_video.mp4")
            animate_face(photo_path, audio_path, output_video)

            return render_template("index.html", image=photo_path, video=output_video, text=history_text)

    return render_template("index.html")

# Генерация текста истории с GPT-4
def generate_history(name):
    try:
        prompt = f"Напиши краткую автобиографию от лица {name} с историческим контекстом."
        response = openai.ChatCompletion.create(
            model="text-davinci-003",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except openai.error.RateLimitError as e:
        return "Превышен лимит запросов. Попробуйте позже."
    except Exception as e:
        return f"Ошибка при запросе к OpenAI: {e}"

# Генерация речи с Google TTS
def generate_voice(text, output_file):
    tts = gTTS(text, lang="ru")
    tts.save(output_file)

# Анимация лица с Wav2Lip
def animate_face(image_path, audio_path, output_file):
    subprocess.run([
        "python", "Wav2Lip/inference.py",
        "--checkpoint_path", "Wav2Lip/checkpoints/wav2lip.pth",
        "--face", image_path,
        "--audio", audio_path,
        "--outfile", output_file
    ])

if __name__ == "__main__":
    app.run(debug=True)