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
        with open("content.txt", "a", encoding="utf-8") as file:
            file.write("\n\nSummary:\n" + summary)

        print("Summary generated and saved.")

    except Exception as e:
        print(f"An error occurred: {e}")

# 安排任务每60秒执行一次
schedule.every(60).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
