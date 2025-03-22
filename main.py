from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from typing import Dict
import aiofiles
import os
import io
import asyncio
import tempfile
import wave
from datetime import datetime
from pydub import AudioSegment

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR='outputs'

def convert_webm_blob_to_wav(webm_blob: bytes, wav_path: str = None) -> str:
    """
    Конвертирует WebM blob в WAV-файл.
    
    Аргументы:
        webm_blob (bytes): Бинарные данные WebM с аудио.
        wav_path (str, optional): Путь для сохранения WAV-файла. Если None, создаётся временный файл.
    
    Возвращает:
        str: Путь к созданному WAV-файлу.
    
    Исключения:
        ValueError: Если blob пустой.
        Exception: Ошибки конвертации.
    """
    if not webm_blob:
        raise ValueError("WebM blob пустой, нет данных для конвертации")

    try:
        # Если путь не указан, создаём временный файл
        if wav_path is None:
            temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            wav_path = temp_wav.name
            should_delete = True
        else:
            should_delete = False

        # Конвертация WebM в WAV
        audio = AudioSegment.from_file(io.BytesIO(webm_blob), format="webm")
        audio.export(wav_path, format="wav")
        print(f"Конвертировано в WAV: {wav_path}")

        return wav_path

    except Exception as e:
        # Удаляем временный файл при ошибке, если он был создан
        if 'wav_path' in locals() and os.path.exists(wav_path) and should_delete:
            os.remove(wav_path)
        raise Exception(f"Ошибка конвертации WebM в WAV: {e}")

def convert_blob_to_wav(blob: bytes, output_path: str, sample_rate: int = 44100, sample_width: int = 2, channels: int = 1) -> None:
    if not blob:
        raise ValueError("Blob пустой, нет данных для конвертации")
    
    if sample_rate <= 0 or sample_width <= 0 or channels <= 0:
        raise ValueError("Некорректные параметры: sample_rate, sample_width и channels должны быть положительными")

    try:
        with wave.open(output_path, 'wb') as wav_file:
            # Устанавливаем параметры WAV-файла
            wav_file.setnchannels(channels)        # Количество каналов
            wav_file.setsampwidth(sample_width)    # Ширина сэмпла (в байтах)
            wav_file.setframerate(sample_rate)     # Частота дискретизации
            wav_file.writeframes(blob)             # Записываем сырые данные
        
        print(f"WAV-файл успешно создан: {output_path}")
    
    except Exception as e:
        raise IOError(f"Ошибка при записи WAV-файла: {str(e)}")

def translate_wav_russian_to_english(wav_path: str) -> str:
    """
    Переводит речь из WAV-файла с русского на английский язык.
    
    Аргументы:
        wav_path (str): Путь к WAV-файлу с русской речью.
    
    Возвращает:
        str: Переведённый текст на английский язык.
    
    Исключения:
        FileNotFoundError: Если WAV-файл не найден.
        ValueError: Если речь не распознана.
        Exception: Общие ошибки обработки.
    """
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"WAV-файл не найден: {wav_path}")

    # Инициализация распознавателя и переводчика
    recognizer = sr.Recognizer()
    translator = GoogleTranslator(source='ru', target='en')

    try:
        # Чтение WAV-файла
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        # Распознавание русской речи
        recognized_text = recognizer.recognize_google(audio_data, language="ru-RU")
        print(f"Распознанный текст (русский): {recognized_text}")

        # Перевод на английский
        translated_text = translator.translate(recognized_text)
        print(f"Переведённый текст (английский): {translated_text}")

        return translated_text

    except sr.UnknownValueError:
        raise ValueError("Не удалось распознать речь в WAV-файле")
    except sr.RequestError as e:
        raise Exception(f"Ошибка сервиса распознавания: {e}")
    except Exception as e:
        raise Exception(f"Ошибка обработки WAV-файла: {e}")

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    output_file = os.path.join(OUTPUT_DIR, f"translation.txt")
    while True:
        try:
            chunk = await websocket.receive()
            if 'text' in chunk:
                print(chunk['text'])
            elif 'bytes' in chunk:
                print('blob got')
                tmp_path = './wavs/'+datetime.now().ctime()+'.wav'
                convert_webm_blob_to_wav(chunk['bytes'], tmp_path)
                translation = translate_wav_russian_to_english(tmp_path)
                await websocket.send_text(translation)

            await websocket.send_json({
                "message": "Message got"
            })
        except WebSocketDisconnect:
            await websocket.close()
        except Exception as e:
            print(str(e))
            await websocket.send_json({"error": str(e)})
            #await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="192.168.200.135", port=8000, reload=True)