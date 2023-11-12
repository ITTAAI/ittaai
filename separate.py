import openai
from openai import OpenAI
import json
from pathlib import Path
openai.api_key = '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'
client = OpenAI(api_key='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')
# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
# 定义全局变量来存储文件名
content=''
def write_to_file(filename, content):
    """
    This function creates a new text file with the given name, writes the provided content to it,
    and stores the file name in a global array.

    :param filename: The name of the file to create.
    :param content: The content to write to the file.
    """
    # 使用global关键字来指明使用外部的全局变量file_names
    global file_names

    # 写入文件的操作
    with open(filename, 'w') as file:
        file.write(content)

    # 将文件名添加到全局变量中
    file_names.append(filename)

#添加到末尾
def append_to_file(filename, content):
    """
    This function appends the given content to the end of the text file specified by filename.
    If the file does not exist, it creates a new one and writes the content to it.

    :param filename: The name of the file to append to.
    :param content: The content to append to the file.
    """
    with open(filename, 'a') as file:  # 'a' mode opens the file for appending
        file.write(content)




def run_conversation(file_names = []):
    # Step 1: send the conversation and available functions to the model
    global content
    with open('content.txt', 'r') as file:
        content = file.read()
    file_names.append("label_axes")
    file_names.append("The onset of sustained economic growth with the Industrial Revolution")
    json_string = json.dumps(file_names)
    print("this current file_name list is "+json_string)
    with open('content.txt', 'r') as file:
        content = file.read()
    messages = [
        {
            "role":"user","content":"this current file_name list is "+json_string
        },
        {
            "role": "user", "content": "plase use one of the two functions.Don't use two functions at the same time。If the following content is a supplement to an existing theme, please use the append_to_file function to add it to the corresponding theme. If this piece of content does not belong to any existing topic, create a topic name of approximately 20 words for it and save it using the write_to_file function."
        },
        {
            "role":"user","content":content
        }
    ]
    tools = [
        {
            "type": "function",
            "function":
                {
                    "name": "write_to_file",
                    "description": "write in a new topic",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "The summary of the new topic",
                            },
                        },
                        "required": ["filename"],
                    },
                },
        },
        {
            "type":"function",
            "function":
                {
                        "name": "append_to_file",
                        "description": "append to a pre-topic",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "filename": {
                                    "type": "string",
                                    "description": "Name of the topic where the new content should be deposited"
                                },
                            },
                            "required": ["filename"],
                        },
                },
        }
    ]
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        tools=tools,
        tool_choice="auto"# auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    print(response_message)
    tools_calls=response_message.tool_calls
    if tools_calls:
        available_functions = {
            "write_to_file": write_to_file,
            "append_to_file":append_to_file,
        }
        for tool_call in tools_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_to_call(
                filename=function_args.get("filename"),
                content=content
            )
    return json.loads(tool_call.function.arguments).get("filename")