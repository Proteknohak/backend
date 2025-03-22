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

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global is_first_chunk
    output_file = os.path.join(OUTPUT_DIR, f"translation.txt")
    while True:
        try:
            chunk = await websocket.receive()
            if 'text' in chunk:
                print(chunk['text'])
            elif 'bytes' in chunk:
                print('blob got')
                tmp_path = './wavs/'+datetime.now().ctime()+'.wav'
                convert_webm_blob_to_wav(chunk['bytes'], tmp_path, is_first_chunk)
                translation = translate_wav_russian_to_english(tmp_path)
                is_first_chunk = False
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


app.include_router(room_router)
app.include_router(user_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="192.168.200.135", port=8000, reload=True)