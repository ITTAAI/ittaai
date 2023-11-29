import asyncio
import json
import logging
import os
import tempfile
import ask_question
import httpx
import vosk_ffmpeg
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from vosk import Model
import subprocess
import separate

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = FastAPI()
origins = ["*"]
stop_event = asyncio.Event()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = ''


@app.on_event("startup")
async def startup_event():
    global api_key
    api_key = load_api_key("OPENAI_API_KEY.txt")


@app.get("/")
async def get():
    return HTMLResponse('')


file_names = []


# ... 其他代码 ...
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    model_big = Model(model_name="vosk-model-en-us-0.42-gigaspeech")
    model_small = Model(model_name="vosk-model-small-en-us-zamia-0.5")
    global api_key
    global file_names
    file_names = []
    # 清除停止事件并重启后台分类任务
    stop_event.clear()
    asyncio.create_task(summary_separate())
    datas = []
    try:
        while True:
            datas.append(await websocket.receive_bytes())
            # 检查数据的长度
            if len(datas[-1]) == 0:
                await websocket.send_text("0 error: Empty audio data received.")
                continue  # 继续下一次循环

            # 创建一个临时文件来保存音频数据
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
                temp_file.write(datas[-1])
                temp_file.flush()  # 确保所有数据都被写入
                # 定义输出文件的路径和名称
                output_txt = temp_file.name.replace(".wav", ".txt")
                try:
                    transcribe = vosk_transcriber_small(temp_file, model_small, output_txt,write_to_file=False)
                    await websocket.send_text(transcribe)
                except Exception as e:
                    print(f"Error during transcription: {e}")
                    await websocket.send_text("Error during transcription. Please try again.")
                # 使用vosk-transcriber转录
            if len(datas) == 10:
                with tempfile.TemporaryDirectory() as temp_dir:
                    # 将音频数据写入临时文件
                    file_paths = []
                    for i, data in enumerate(datas):
                        temp_file_path = f"{temp_dir}/file{i}.ogg"
                        with open(temp_file_path, "wb") as f:
                            f.write(data)
                        file_paths.append(temp_file_path)

                    # 创建文件列表
                    files_txt_path = f"{temp_dir}/files.txt"
                    with open(files_txt_path, 'w') as f:
                        for file_path in file_paths:
                            f.write(f"file '{file_path}'\n")

                    # 使用ffmpeg合并音频文件
                    output_path = f"{temp_dir}/output.ogg"
                    subprocess.run(
                        ["ffmpeg", "-f", "concat", "-safe", "0", "-i", files_txt_path, "-c", "copy", output_path])
                    # 在这里可以进行对output_path指向的合并后的文件的操作
                    try:
                        transcribe = vosk_transcriber_small(temp_file, model_big, output_txt)
                        print(transcribe)
                    except Exception as e:
                        print(f"Error during transcription: {e}")
                        await websocket.send_text("Error during transcription. Please try again.")

    except WebSocketDisconnect:
        print("Client disconnected")
        stop_event.set()
    except Exception as e:
        print(e)


class FormData(BaseModel):
    q: str
    service: str


@app.post("/submit-form")
async def submit_form(data: FormData):
    print(f"Received form data: {data}")
    content = ""
    if os.path.exists('content.txt'):
        with open('content.txt', 'r') as file:
            content = file.read()

    if data.service == "gpt":
        # 如果用户选择了gpt，我们就调用GPT-3的服务
        return await handle_gpt_service(data.q)
    elif data.service == "claude":
        # 如果用户选择了claude，我们就调用Claude的服务
        # 注意: 你需要实现这个函数!
        return await handle_claude_service(data.q)
    else:
        return {"error": "Invalid service selected"}


@app.get("/get_summary")
async def get_summary():
    try:
        with open("summary.txt", "r", encoding="utf-8") as file:
            content = file.read()
        return JSONResponse(content={"summary": content})
    except FileNotFoundError:
        return JSONResponse(content={"error": "File not found"}, status_code=404)


# 运行应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)


# 处理GPT-3服务的函数
async def handle_gpt_service(q: str):
    try:
        # 从content.txt中读取内容
        with open("content.txt", "r", encoding="utf-8") as file:
            content = file.read()
        try:
            reply = await call_gpt_async(q)
            return {"data": reply}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        return {"error": str(e)}


async def call_gpt_async(q: str):
    loop = asyncio.get_running_loop()
    global api_key
    # 将同步的 openai 调用包装到线程池中运行
    response = await loop.run_in_executor(None, ask_question.ask, q, api_key
                                          )
    return response.choices[0].message['content']


# 需要实现的处理Claude服务的函数
async def handle_claude_service(q: str, content: str):
    # 构造到云函数的请求
    url = "https://asvx1c.laf.dev/claude-chat"
    q = "this"
    params = {"question": q, "conversationId": 1}  # 如果content是会话ID的话

    # 发送异步HTTP GET请求到云函数
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    # 检查请求是否成功
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Claude API request failed.")

    # 解析并返回结果
    result = response.json()
    return {"Claude_response": result.get("msg", "")}


@app.get("/")
async def summary_separate():
    loop = asyncio.get_running_loop()
    # 在线程池中运行阻塞函数
    global file_names
    await asyncio.sleep(120)
    while not stop_event.is_set():
        file_names.append(await loop.run_in_executor(None, separate.run_conversation, api_key))
        await asyncio.sleep(300)


def load_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()


# 使用vosk-transcriber转录
async def vosk_transcriber_small(temp_file, model_name, output_txt,write_to_file=True):
    transcribe = vosk_ffmpeg.vosk_ffmpeg(temp_file.name, model_name)
    transcribe_json = json.loads(transcribe)
    transcribe = transcribe_json['text']
    with open(output_txt, "w") as file:
        file.write(transcribe)
    # 读取转录后的文件并通过WebSocket发送
    # 写入更新后的内容到content.txt
    if write_to_file:
        with open('content.txt', 'a') as file:
            file.write(transcribe)
    return transcribe
