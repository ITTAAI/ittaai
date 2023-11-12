import os
import subprocess
import tempfile
import openai
import asyncio
import seperate
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from vosk import Model, KaldiRecognizer, SetLogLevel
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import logging

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
content = 'This is what the professor said'

openai.api_key = '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'


@app.get("/")
async def get():
    return HTMLResponse('')


# ... 其他代码 ...
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    model = Model(lang="en-us")
    with open("summary.txt", "w", encoding="utf-8") as file:
        file.write('')
    with open("content.txt", "w", encoding="utf-8") as file:
        file.write('')
    global content
    try:
        while True:
            data = await websocket.receive_bytes()
            # 检查数据的长度
            if len(data) == 0:
                await websocket.send_text("0 error: Empty audio data received.")
                continue  # 继续下一次循环

            # 创建一个临时文件来保存音频数据，设置delete为False以保留文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(data)
                temp_file.flush()  # 确保所有数据都被写入

                # 定义输出文件的路径和名称
                output_txt = temp_file.name.replace(".wav", ".txt")

                # 使用vosk-transcriber转录
                try:
                    transcribe_command = f'vosk-transcriber  --model-name vosk-model-small-en-us-zamia-0.5 --input "{temp_file.name}" --output "{output_txt}"'
                    subprocess.run(transcribe_command, shell=True, check=True)

                    # 读取转录后的文件并通过WebSocket发送
                    with open(output_txt, 'r') as txt_file:
                        transcription = txt_file.read()
                        await websocket.send_text(transcription)
                        content += transcription
                        # 写入更新后的内容到content.txt
                        with open('content.txt', 'a') as file:
                            file.write(content)
                        content = ''
                except Exception as e:
                    print(f"Error during transcription: {e}")
                    await websocket.send_text("Error during transcription. Please try again.")
    except WebSocketDisconnect:
        print("Client disconnected")
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
            reply = await call_gpt_async(content, q)
            return {"data": reply}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        return {"error": str(e)}

async def call_gpt_async(content: str, q: str):
    loop = asyncio.get_running_loop()
    # 将同步的 openai 调用包装到线程池中运行
    response = await loop.run_in_executor(
        None,  # None 默认使用 ThreadPoolExecutor
        lambda: openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": content},
                {"role": "user", "content": q}
            ],
            max_tokens=2000,
        )
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
async def summary_seperat():
    loop = asyncio.get_running_loop()
    # 在线程池中运行阻塞函数
    await loop.run_in_executor(None, seperate.run_conversation())
    # 阻塞函数完成后返回响应

