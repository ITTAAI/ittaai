from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import shutil  # 导入shutil模块来处理文件删除
from fastapi.responses import HTMLResponse
import tempfile
import subprocess
app = FastAPI()
import os
import openai
openai.api_key = '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'
@app.get("/")
async def get():
    return HTMLResponse(html)

# ... 其他代码 ...

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
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
                        content+=transcription
                        count+=1
                        if count==88 :
                            completion = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content":content},
                                    {"role": "user","content": "Please summarize the content I provide without changing the perspective and keep it within 300 words."}

                                ]
                            )
                            content=(completion.choices[0].message)
                            count=0
                except Exception as e:
                    print(f"Error during transcription: {e}")
                    await websocket.send_text("Error during transcription. Please try again.")

    except WebSocketDisconnect:
        print("Client disconnected")
