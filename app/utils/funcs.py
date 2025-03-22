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

def extract_webm_headers(webm_blob: bytes, max_header_size: int = 200) -> bytes:
    """
    Извлекает заголовки из первого WebM blob (примерно до начала аудиоданных).
    Возвращает байты заголовков.
    """
    cluster_start = webm_blob.find(b'\x1F\x43\xB6\x75')
    if cluster_start == -1:
        return webm_blob[:max_header_size]
    return webm_blob[:cluster_start]

def convert_webm_blob_to_wav(webm_blob: bytes, wav_path: str = None, is_first_chunk: bool = False) -> str:
    """
    Конвертирует WebM blob в WAV-файл с использованием заголовков, если нужно.
    """
    global webm_headers

    if not webm_blob:
        raise ValueError("WebM blob пустой, нет данных для конвертации")

    if wav_path is None:
        temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav_path = temp_wav.name
        should_delete = True
    else:
        should_delete = False

    # Инициализируем переменные вне try, чтобы они были доступны в except
    temp_webm_path = None

    try:
        # Если это первый чанк, сохраняем заголовки
        if is_first_chunk:
            webm_headers = extract_webm_headers(webm_blob)
            fixed_blob = webm_blob
        else:
            if webm_headers is None:
                raise ValueError("Заголовки WebM не инициализированы, первый чанк не обработан")
            fixed_blob = webm_headers + webm_blob

        # Сохраняем "исправленный" WebM во временный файл
        temp_webm = tempfile.NamedTemporaryFile(suffix=".webm", delete=False)
        temp_webm_path = temp_webm.name
        with open(temp_webm_path, "wb") as f:
            f.write(fixed_blob)
        print(f"Сохранён WebM-чанк: {temp_webm_path}")

        # Конвертируем в WAV
        audio = AudioSegment.from_file(temp_webm_path, format="webm")
        audio.export(wav_path, format="wav")
        print(f"Конвертировано в WAV: {wav_path}")

        # Удаляем временный WebM-файл
        if os.path.exists(temp_webm_path):
            os.remove(temp_webm_path)

        return wav_path
    except Exception as e:
        # Очистка только существующих файлов
        if os.path.exists(wav_path) and should_delete:
            os.remove(wav_path)
        if temp_webm_path and os.path.exists(temp_webm_path):
            os.remove(temp_webm_path)
        raise Exception(f"Ошибка конвертации WebM в WAV: {e}")

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
