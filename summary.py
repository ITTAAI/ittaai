import time

import openai
import schedule

# 配置您的OpenAI API密钥
openai.api_key = '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'


def job():
    try:
        # 从文件读取内容
        with open("content.txt", "r", encoding="utf-8") as file:
            content = file.read()

        # 向GPT-3.5模型发送请求
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": content},
                {"role": "user",
                 "content": "Please summarize the content I provide without changing the perspective and keep it within 300 words."}
            ]
        )

        # 获取生成的摘要
        summary = completion['choices'][0]['message']['content']

        # 将摘要写入文件
        with open("summary.txt", "w", encoding="utf-8") as file:
            file.write(summary)

        # 将摘要追加到内容文件
        # 首先，我们读取文件内容并检查其长度
        with open("content.txt", "r", encoding="utf-8") as file:
            content = file.read()

        # 如果字符数超过20,000，我们覆盖文件内容为summary
        if len(content) > 10000:
            with open("content.txt", "w", encoding="utf-8") as file:
                file.write(summary)

        print("Summary generated and saved.")

    except Exception as e:
        print(f"An error occurred: {e}")


time.sleep(300)
# 安排任务每60秒执行一次
schedule.every(300).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
ç