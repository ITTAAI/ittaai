import openai
from openai import OpenAI
import json
import separate
from pathlib import Path
openai.api_key = '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'
client = OpenAI(api_key='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')
# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
# 定义全局变量来存储文件名
content=''
print(separate.run_conversation())
if __name__ == "__main__":
    print(())