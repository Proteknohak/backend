from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.room import router as room_router
from app.api.user import router as user_router

from app.utils.funcs import *

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

webm_headers = None
organizer_ws = None
is_first_chunk = True

wsockets: list[tuple[WebSocket, str]] = []

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    global organizer_ws, webm_headers, wsockets
    await websocket.accept()
    lang = await websocket.receive_text()  # Получаем язык перевода
    is_creator = int(await websocket.receive_text())  # 1 для организатора, 0 для участника

    if is_creator:
        if organizer_ws is not None:
            await websocket.send_json({"error": "Организатор уже подключён"})
            await websocket.close()
            return
        organizer_ws = websocket
        is_first_chunk = True  # Локальный флаг для организатора
        print("Организатор подключён")
    else:
        wsockets.append((websocket, lang))
        print(f"Участник подключён, язык: {lang}")

    try:
        while True:
            chunk = await websocket.receive()
            if 'text' in chunk:
                print(f"Получен текст: {chunk['text']}")
            elif 'bytes' in chunk and is_creator:  # Только организатор отправляет аудио
                print("blob got")
                tmp_path = f'./wavs/{datetime.now().ctime()}.wav'
                
                # Конвертируем WebM в WAV
                convert_webm_blob_to_wav(chunk['bytes'], tmp_path, is_first_chunk)
                
                # Рассылаем перевод всем участникам
                for wsocket, participant_lang in wsockets[:]:  # Копируем список для безопасного перебора
                    try:
                        translation = translate_wav_russian_to_english(tmp_path, participant_lang)
                        tts = gTTS(text=translation, lang=participant_lang)
                        
                        mp3_buffer = io.BytesIO()
                        tts.write_to_fp(mp3_buffer)
                        mp3_buffer.seek(0)
                        
                        audio = AudioSegment.from_mp3(mp3_buffer)
                        wav_buffer = io.BytesIO()
                        audio.export(wav_buffer, format="wav")
                        wav_buffer.seek(0)

                        wav_bytes = wav_buffer.getvalue()
                        await wsocket.send_bytes(wav_bytes)
                        
                        mp3_buffer.close()
                        wav_buffer.close()
                    except Exception as e:
                        print(f"Ошибка отправки участнику: {e}")
                        if wsocket in [ws[0] for ws in wsockets]:
                            wsockets.remove((wsocket, participant_lang))

                # Очищаем временный файл и обновляем флаг
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                is_first_chunk = False

    except WebSocketDisconnect:
        if is_creator:
            organizer_ws = None
            webm_headers = None  # Сбрасываем заголовки при отключении организатора
            # Закрываем всех участников
            for wsocket, _ in wsockets[:]:
                try:
                    await wsocket.close()
                except:
                    pass
            wsockets.clear()
            print("Организатор отключён, комната очищена")
        else:
            if (websocket, lang) in wsockets:
                wsockets.remove((websocket, lang))
            print(f"Участник отключён, язык: {lang}")
        await websocket.close()
    except Exception as e:
        print(f"Ошибка: {e}")
        if 'Cannot call "receive" once a disconnect message has been received.' == str(e):
            raise e
        await websocket.send_json({"error": str(e)})

app.include_router(room_router)
app.include_router(user_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)