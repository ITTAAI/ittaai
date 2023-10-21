import requests
import json

def test_cloud_function():
    # 云函数的URL
    url = 'https://asvx1c.laf.dev/claude-chat'

    # 您想询问的问题
    content = "What would you say would happen to the demand for phones? It would go down, I said except we're all addicted to phones so really tough to get away from it. Yeah, but for any good doesn't have to be phones. If if your tastes change or your preferences, and you just don't like that good anymore for whatever reason the demand decreases, then we would shift the curve to the left. If this is t one, this is my original .. And again, nothing happens to the price, but you change in your mind. You don't like this product anymore. So at at any given price, you are selling less. There's more examples. Let's say population increases, sample in our political arena. All the people in north gaza were ordered to go south. Thousands of people have traveled south. Gaza is completed all along with people, because you won't be the people in the streets and always everywhere. They don't have housing for so many people. The population increases to whatever matter what happens to demand, shift the rights to the right?"

    # 可选的会话ID，如果有的话
    conversation_id = "教授讲了什么"

    # 请求参数
    payload = {
        'content': content,
        'question': conversation_id  # 如果没有conversationId可以设置为None或完全删除此行
    }

    # 发送GET请求
    response = requests.get(url, params=payload)

    # 确认是否收到了有效响应
    if response.status_code == 200:
        # 解析并打印响应内容
        data = response.json()
        print(json.dumps(data, indent=4))
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

# 执行测试函数
if __name__ == "__main__":
    test_cloud_function()
