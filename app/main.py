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
is_first_chunk = True
wsockets = []

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    lang = await websocket.receive_text()
    is_creator = int(await websocket.receive_text())
    global is_first_chunk
    global wsockets
    if is_creator:
        wsockets.append(websocket)
    else:
        while True:
            try:
                chunk = await websocket.receive()
                if 'text' in chunk:
                    print(chunk['text'])
                elif 'bytes' in chunk:
                    print('blob got')
                    tmp_path = './wavs/'+datetime.now().ctime()+'.wav'
                    convert_webm_blob_to_wav(chunk['bytes'], tmp_path, is_first_chunk)
                    translation = translate_wav_russian_to_english(tmp_path, lang)
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                    is_first_chunk = False
                    tts = gTTS(text=translation, lang=lang)
            
                    mp3_buffer = io.BytesIO()
                    tts.write_to_fp(mp3_buffer)
                    mp3_buffer.seek(0)
                    
                    audio = AudioSegment.from_mp3(mp3_buffer)
                    wav_buffer = io.BytesIO()
                    audio.export(wav_buffer, format="wav")
                    wav_buffer.seek(0)

                    wav_bytes = wav_buffer.getvalue()                
                    
                    await websocket.send_bytes(wav_bytes)
                    
                    mp3_buffer.close()
                    wav_buffer.close()

            except WebSocketDisconnect:
                await websocket.close()
            except Exception as e:
                print(str(e))
                if 'Cannot call "receive" once a disconnect message has been received.' == str(e):
                    raise e
            #await websocket.send_json({"error": str(e)})
            #await websocket.close()

app.include_router(room_router)
app.include_router(user_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)