import subprocess
import tempfile

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
import openai

openai.api_key = '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'


@app.get("/")
async def get():
    return HTMLResponse('')


# ... 其他代码 ...

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    content = ''
    count = 0
    await websocket.accept()
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
                    transcribe_command = f'vosk-transcriber --input "{temp_file.name}" --output "{output_txt}"'
                    subprocess.run(transcribe_command, shell=True, check=True)

                    # 读取转录后的文件并通过WebSocket发送
                    with open(output_txt, 'r') as txt_file:
                        transcription = txt_file.read()
                        await websocket.send_text(transcription)
                        content += transcription
                        count += 1
                        if count == 88:
                            completion = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": content},
                                    {"role": "user",
                                     "content": "Please summarize the content I provide without changing the perspective and keep it within 300 words."}
                                ]
                            )
                            content = (completion.choices[0].message)
                            count = 0
                            # 写入更新后的内容到content.txt
                            with open('content.txt', 'w') as file:
                                file.write(content)
                except Exception as e:
                    print(f"Error during transcription: {e}")
                    await websocket.send_text("Error during transcription. Please try again.")

    except WebSocketDisconnect:
        print("Client disconnected")


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
        return await handle_gpt_service(data.q, content)
    elif data.service == "claude":
        # 如果用户选择了claude，我们就调用Claude的服务
        # 注意: 你需要实现这个函数!
        return await handle_claude_service(data.q, content)
    else:
        return {"error": "Invalid service selected"}


# 处理GPT-3服务的函数
async def handle_gpt_service(q: str, content: str):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": content},
                {"role": "user", "content": q}
            ]
        )
        reply = response.choices[0].message
        return {"GPT-3_response": reply}
    except Exception as e:
        return {"error": str(e)}


# 需要实现的处理Claude服务的函数
async def handle_claude_service(q: str, content: str):
    # 构造到云函数的请求
    url = "https://asvx1c.laf.dev/claude-chat"
    q = "this"
    params = {"question": q, "conversationId": content}  # 如果content是会话ID的话

    # 发送异步HTTP GET请求到云函数
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    # 检查请求是否成功
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Claude API request failed.")

    # 解析并返回结果
    result = response.json()
    return {"Claude_response": result.get("msg", "")}
