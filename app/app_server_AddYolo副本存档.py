import requests  # 用于发送 HTTP 请求
import json  # 用于处理 JSON 数据
import gradio as gr  # 用gradio创建图形用户界面
import io  # 用于处理字节流
from PIL import Image
import numpy as np
# import cv2
# import paddlex as pdx
# from paddlex.det import transforms


# 文心AI的API Key和Secret Key，用于链接文心大模型
SC_API_KEY = "Ge1lZ7If6RUzKuIqvpqR5MY2"
SC_SECRET_KEY = "cEUo45RrQAgBjr1oVg8Y9kxG155fYERB"

# salesforce BLIP 的inference API reference KEY
API_URL_BLIP = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
headers_BLIP = {"Authorization": "Bearer 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"}

# 烟火检测（判断）API reference KEY
API_URL_FIRE_VIT = "https://api-inference.huggingface.co/models/EdBianchi/vit-fire-detection"
headers_FIRE_VIT = {"Authorization": "Bearer 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"}

# 获取百度AI的access_token（输入SC_API_KEY 和 SC_SECRET_KEY，输出access_token）
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


# 自定义的知识库字符串，用于个性化定制文心大模型
knowledge_base = "林业管理和应急消防的专业知识"  

# # 为应对多次分析请求，初始化一个列表来存储所有生成的文本。
# generated_texts = []

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
                    "要根据下面的描述给出一个解决方案，（要求回答中只需含有解决方案，并且方案应该主要面向林业消防部分或者林业安全员提出）：" + 
                    input_text,
            }
        ]
    })
    headers = { # 设置 HTTP 请求的头部信息
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload) # 发送 HTTP POST 请求，返回一个response对象
    result = response.json().get("result")  # 从response对象中提取出 JSON 数据（回答文本）
    print("WENXIN RESPONSE:\n" + result + "\n") # log for debugging
    return result

def elaborate_description(input_text):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=" + get_access_token()
    payload = json.dumps({  # 将 Python 对象转换编码成 JSON 字符串
        "messages": [   # 拼接出完整query，包含三部分：引导词、知识库、场景描述
            {
                "role": "user",
                "content": "请你根据下面的描述文字，合理地扩写（注意扩写后的文字应该是客观、冷静的、描述性的林业管理术语）不应该有附加的原因分析、措施建议和总结"  + 
                    input_text,
            }
        ]
    })
    headers = { # 设置 HTTP 请求的头部信息
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload) # 发送 HTTP POST 请求，返回一个response对象
    result = response.json().get("result")  # 从response对象中提取出 JSON 数据（回答文本）
    print("WENXIN RESPONS(ELABORATE):\n" + result + "\n") # log for debugging
    return result


# BLIP API的调用函数
def BLIP_query(image_data):
    response = requests.post(API_URL_BLIP, headers=headers_BLIP, data=image_data)
    # 在BLIP_query调用后添加这行
    return response.json()

# 图片分析函数
# INPUT：用户上传的图片
# OUTPUT：图片分析文本
def image_analysis(input_image):

    # # DEBUG: 保存input_image到本地
    # cv2.imwrite('temp.jpg', input_image)
    # print("IMAGE ARRAY MAX VALUE" + str(input_image.max())) # 255

    # 将输入的input_image(numpy数组类型)转成query函数可以接受的Bytes类型
    img = Image.fromarray(input_image.astype(np.uint8))  # 需要转换为 uint8，范围 [0, 255]    
    img_byte_arr = io.BytesIO()  # 创建一个字节流对象
    img.save(img_byte_arr, format='PNG')  # 将图像保存到字节流中，可以选择不同的格式，例如 'JPEG'，这里用 'PNG'
    img_byte_arr = img_byte_arr.getvalue()  # 获取字节流的值

    # 调用 BLIP_query 函数
    output = BLIP_query(img_byte_arr)

    # # DEBUG
    print("✨✨✨✨✨✨✨✨✨BLIP output:", output)

    # # DEBUG
    # print("TYPE OF OUTPUT OF QUERY\n")
    # print(type(output)) # list
    
    # 取出列表的0号元素，然后用 ['generated_text'] 取出字典中的值
    newly_generated_text = output[0]['generated_text'] 
    # generated_texts.append(newly_generated_text)
    # generated_text = generated_texts[-1] #  取列表的最后一个元素，确保每次都是最新的文本

    # 将newly_generated_text传给文心API，进行扩写
    elaborated_text = elaborate_description(newly_generated_text)

    # 最后，返回生成的文本
    return elaborated_text



# 目标检测函数
# INPUT：用户上传的图片
# OUTPUT：图片经目标检测的返图
def detect(input_image):
    # # 调用已经训练好的`best_model`进行预测
    # model = pdx.load_model('../best_model')

    # # 将input_image转成.jpg格式，保存在../目录下

    # # 将输入的input_image(numpy数组类型)转成query函数可以接受的Bytes类型
    # img = Image.fromarray(input_image.astype(np.uint8))  # 需要转换为 uint8，范围 [0, 255]
    # img_byte_arr = io.BytesIO()  # 创建一个字节流对象
    # img.save(img_byte_arr, format='JPG')  # 将图像保存到字节流中，可以选择不同的格式，例如 'JPEG'，这里用 'PNG'
    # img_byte_arr = img_byte_arr.getvalue()  # 获取字节流的值

    # result = model.predict(img_byte_arr)
    
    # # 将result 进行可视化，并保存到指定路径
    # pdx.det.visualize(image_name, result, threshold=0.05, save_dir='../')
    
    # # 重新打开图像并返回
    # output_image = Image.open('../visualize_test_image.jpg')
    
    # FILL TEMPORAIRLY to test the front-end look
    output_image = Image.open('../visualized_test_image_temp.jpg')

    return output_image


def judge_query(image_data):
    response = requests.post(API_URL_FIRE_VIT, headers=headers_FIRE_VIT, data=image_data)
    return response.json()

def judge(input_image):
    # 将输入的input_image(numpy数组类型)转成query函数可以接受的Bytes类型
    img = Image.fromarray(input_image.astype(np.uint8))  # 需要转换为 uint8，范围 [0, 255]    
    img_byte_arr = io.BytesIO()  # 创建一个字节流对象
    img.save(img_byte_arr, format='PNG')  # 将图像保存到字节流中，可以选择不同的格式，例如 'JPEG'，这里用 'PNG'
    img_byte_arr = img_byte_arr.getvalue()  # 获取字节流的值

    output = judge_query(img_byte_arr)

    # # 检查输出是否包含错误信息
    # if 'error' in output:
    #     # 处理错误情况，例如返回错误信息或重试请求
    #     return f"Error: {output['error']}"

    # # DEBUG
    print("✨✨✨✨✨✨✨✨✨VIT output:", output)

    # 如果没有错误，则格式化输出
    formatted_output = "烟火元素置信度分析结果：\n"

    # 提取出output中label值为Normal、Fire、Smoke的置信度
    for item in output:
        if item['label'] == 'Normal':
            normal_score = item['score']
            formatted_output += f"Normal置信度: {item['score']}\n"
        elif item['label'] == 'Fire':
            fire_score = item['score']
            formatted_output += f"Fire置信度: {item['score']}\n"
        elif item['label'] == 'Smoke':
            smoke_score = item['score']
            formatted_output += f"Smoke置信度: {item['score']}\n"

    formatted_output += "\n烟火目标判断结果：\n"
    if fire_score > normal_score or smoke_score > normal_score:
        formatted_output += "⚠️存在火情"
    else:
        formatted_output += "🍃不存在火情"

    judgement_output = formatted_output

    # 最后，返回生成的文本
    return judgement_output


# 在Gradio UI中增加新的组件
with gr.Blocks() as demo:
    with gr.Row():
        image_input = gr.Image()
        analysis_result = gr.Textbox(label="分析结果")
    analysis_button = gr.Button("分析图片")
        
    with gr.Tab("建议"):
        text_output = gr.Textbox(label="输出")
    text_button = gr.Button("获取建议")

    with gr.Tab("烟火元素置信度分析(适用林火)"):  # 新增Row
        judge_image_output = gr.Textbox(label="分析判断结果", image_mode='fixed', width=600)
    judge_button = gr.Button("分析判断图片")
        
    with gr.Tab("烟火目标检测可视化(适用林火)"):  # 新增Row
        detected_image_output = gr.Image(label="目标检测结果", image_mode='fixed', width=600)  # 新增图像输出组件
    detect_button = gr.Button("显示目标检测结果")  # 新增按钮
    
    analysis_button.click(image_analysis, inputs=image_input, outputs=analysis_result) # 将按钮与image_analysis函数关联
    text_button.click(main_app, inputs=analysis_result, outputs=text_output) # 将按钮与main_app函数关联
    detect_button.click(detect, inputs=image_input, outputs=detected_image_output)  # 将按钮与detect函数关联
    judge_button.click(judge, inputs=image_input, outputs=judge_image_output)  # 将按钮与judge_query函数关联

demo.launch()