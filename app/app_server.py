import requests
import json
import gradio as gr

SC_API_KEY = "zRzIr6rPTs0cGEvWt5G6rBpR"
SC_SECRET_KEY = "bZ5mIN37G304K1fNUwOvZSkoMStbi5Gh"

def main_app(input_text):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=" + get_access_token()
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": "假如你是一个专业林业工作者，你要根据下面的描述给出一个解决方案，并且回答中只需含有解决方案："+input_text,
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    result = response.json().get("result")  
    print(result)
    return result

def get_access_token():
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={SC_API_KEY}&client_secret={SC_SECRET_KEY}"
    payload = ""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    return str(response.json().get("access_token"))


# 你的程序：
def image_analysis(input_image):
    # 输入：图片
    # 输出：字符串
    pass



### Gradio UI ###
with gr.Blocks() as demo:
    with gr.Row():
        image_input = gr.Image()
        analysis_result = gr.Textbox(label="分析结果")
    analysis_button = gr.Button("分析图片")
        
    with gr.Tab("建议"):
        text_output = gr.Textbox(label="输出")
        text_button = gr.Button("获取建议")
    
        
    analysis_button.click(image_analysis, inputs=image_input, outputs=analysis_result)
    text_button.click(main_app, inputs=analysis_result, outputs=text_output)

demo.launch()