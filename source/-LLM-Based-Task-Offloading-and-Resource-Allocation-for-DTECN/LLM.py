#coding=UTF-8
from openai import OpenAI
from llmenv import Environment
import numpy as np
import copy
import json


query_text = "You are a mathematical tool to predict some models. You need to predict actions for a given state. The following is a dataset you can use for prediction. You need to predict the action matrix for the last given state matrix based on the dataset. Please output the action matrix directly without any other information.\n"

lane_num = 3
n_veh = 11
task_num = 3
# 读取多行字典数据
data = []
with open(f'sample_{n_veh}_-0.5.txt', 'r', encoding='utf-8') as file:
    # 使用 readline() 按行读取文件内容
    content = file.read()  # 读取所有内容
    dictionaries = content.split('\n}\n')  # 按字典分割
    
    for dict_str in dictionaries:
        if dict_str.strip():  # 确保不读取空字符串
            dict_str = dict_str + '}'  # 补全每个字典的闭合括号
            data.append(json.loads(dict_str.strip()))  # 解析为字典并添加到列表

# 打印读取的数据
#print(data)

for dic in data:
    for value in dic.values():
      query_text += value
    query_text += '\n'

context = query_text


env = Environment(lane_num, n_veh, task_num)
s = env.reset()

num = 1
mean_delay, mean_Q_sys, mean_E_sys, mean_E_q = [], [], [], []
res = []
for i in range(1):
    s = np.round(s, 1).tolist()
    query_text += f'state is {s}, then action is'

    client = OpenAI(
    base_url = "https://integrate.api.nvidia.com/v1",
    api_key = "your api key"
    )

    completion = client.chat.completions.create(
    model='meta/llama-3.1-8b-instruct',
    messages=[{"role":"user","content":query_text}],
    temperature=0.2,
    top_p=0.7,
    max_tokens=26200,
    stream=True
    )

    pro = ''
    print('current epoch:', num)
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            a_m = chunk.choices[0].delta.content
            #print(chunk.choices[0].delta.content, end="")
            pro += a_m
            #action = chunk.choices[0].delta.content.split
    action = json.loads(pro)
    s_, _, _ = env.step(action)
    s = s_
    mean_delay.append(env.tk_delay)
    mean_Q_sys.append(env.Q_sys)
    mean_E_sys.append(env.E_sys)
    mean_E_q.append(env.E_q)
    res.append(np.sum(env.action_task))
    num += 1

print('delay:', np.mean(mean_delay), '\nQ_sys:', np.mean(mean_Q_sys), '\nE_sys:', np.mean(mean_E_sys), '\nE_q:', np.mean(mean_E_q), '\nresource:', np.mean(res))





