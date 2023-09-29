import requests  # 用于发送 HTTP 请求
import json  # 用于处理 JSON 数据
import gradio as gr  # 用gradio创建图形用户界面
import io  # 用于处理字节流
from PIL import Image
import numpy as np
import cv2

# 百度AI的API Key和Secret Key，用于链接文心大模型
SC_API_KEY = "zRzIr6rPTs0cGEvWt5G6rBpR"
SC_SECRET_KEY = "bZ5mIN37G304K1fNUwOvZSkoMStbi5Gh"

# 连接 salesforce BLIP 的inference API
API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
blip_headers = {"Authorization": "Bearer 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"}

# 自定义的知识库字符串，用于个性化定制文心大模型
knowledge_base = ""  

# 文心API的调用函数
# INPUT：用户的输入文本
# OUTPUT：文心的回答文本
def main_app(input_text):
    # 拼接 URL，文心的base_url + access token, 只有拥有有效的access_token，才能成功调用文心API。
    # get_access_token()函数会发送一个 HTTP POST 请求到百度 获取access_token。 具体的实现在下面。
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=" + get_access_token()
    payload = json.dumps({  # 将 Python 对象转换编码成 JSON 字符串
        "messages": [   # 拼接出完整query，包含三部分：引导词、知识库、场景描述
            {
                "role": "user",
                "content": "假如你是一个专业林业安全管理员，熟知：" + knowledge_base + 
                    "要根据下面的描述给出一个解决方案，并且回答中只需含有解决方案：" + 
                    input_text,
            }
        ]
    })
    headers = { # 设置 HTTP 请求的头部信息
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload) # 发送 HTTP POST 请求，返回一个response对象
    result = response.json().get("result")  # 从response对象中提取出 JSON 数据（回答文本）
    print("WENXIN RESPONSE:\n" + result + "\n")
    return result

# 获取百度AI的access_token
# INPUT：无，但需要使用到前面定义的 SC_API_KEY 和 SC_SECRET_KEY
# OUTPUT：access_token
def get_access_token(): 
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={SC_API_KEY}&client_secret={SC_SECRET_KEY}" # 拼接 request URL
    payload = ""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload) # 发送 HTTP POST 请求，返回一个response对象
    print("ACCESS_TOKEN OBTAINED: \n" + response.text + "\n")
    return str(response.json().get("access_token"))


# def query(filename):
#     with open(filename, "rb") as f:
#         data = f.read()
#     response = requests.post(API_URL, headers=blip_headers, data=data)
#     return response.json()

def query(image_data):
    response = requests.post(API_URL, headers=blip_headers, data=image_data)
    return response.json()

# 图片分析函数
# INPUT：用户上传的图片
# OUTPUT：图片分析文本
def image_analysis(input_image):

    # 如果 input_image 是 BGR，转换为 RGB
    input_image = input_image[:, :, ::-1]  # ::-1 会将最后一个维度（颜色通道）反转

    # DEBUG: 保存input_image到本地
    cv2.imwrite('temp.jpg', input_image)


    # 将输入的input_image(numpy数组类型)转成query函数可以接受的Bytes类型
    # img = Image.fromarray((input_image * 255).astype(np.uint8))  # Gradio 返回的图像数组通常是 float32 类型，范围在 [0, 1] 之间，需要转换为 uint8，范围 [0, 255]    
    img = Image.fromarray(input_image)  # 此时 input_image 应该是 RGB 格式，uint8 类型，范围 [0, 255]

    img_byte_arr = io.BytesIO()  # 创建一个字节流对象
    
    img.save(img_byte_arr, format='PNG')  # 将图像保存到字节流中，可以选择不同的格式，例如 'JPEG'，这里用 'PNG'
    
    img_byte_arr = img_byte_arr.getvalue()  # 获取字节流的值

    # 调用 query 函数
    output = query(img_byte_arr)

    # # DEBUG
    # print("TYPE OF OUTPUT OF QUERY\n")
    # print(type(output)) # list

    generated_text = output[0]['generated_text']  # 取出列表的0号元素，然后用 ['generated_text'] 取出字典中的值
    # 最后，返回生成的文本
    return generated_text


### Gradio UI ###
with gr.Blocks() as demo:
    with gr.Row():
        image_input = gr.Image()
        # #DEBUG
        # print("DEBUG: image_input type is:")
        # print(type(image_input)) # <class 'gradio.components.image.Image'>
        analysis_result = gr.Textbox(label="分析结果")
    analysis_button = gr.Button("分析图片")
        
    with gr.Tab("建议"):
        text_output = gr.Textbox(label="输出")
        text_button = gr.Button("获取建议")
    
    analysis_button.click(image_analysis, inputs=image_input, outputs=analysis_result)
    text_button.click(main_app, inputs=analysis_result, outputs=text_output)

demo.launch()