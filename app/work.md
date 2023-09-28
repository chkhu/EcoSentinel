# [EcoSentinel](https://github.com/chkhu/EcoSentinel#ecosentinel)





## 对接文心一言模型

进入文心一言官网，在文心一言中创建应用，付费并获取api

![image-20230929001148973](https://cdn.jsdelivr.net/gh/SankHyan24/image1/img/image-20230929001148973.png)

![image-20230929001330204](https://cdn.jsdelivr.net/gh/SankHyan24/image1/img/image-20230929001330204.png)

下面的api key和secret key以后会用到

## 用python获取access token

获取接口访问凭证 access_token 。根据第1步获取的 API Key 和 Secret Key ，调用[获取access_token](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Ilkkrb0i5)接口获取 access_token ，通过 access_token 鉴权调用者身份。

这里将这一步封装为一个函数：

```python
import requests
import json
SC_API_KEY= "your key"
SC_SECRET_KEY= "your key"
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
```

因为我们的问题是基于一个护林员的知识基础的，所以在这里构建request的时候在pyload的回答中加入相应描述。并在最后将回答抓包并返回。

```python
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
```

## 部署GRADIO前端界面

 目前的程序接口只能在命令行执行，需要搭配前端。这里我们使用gradio作为前端工具进行部署。

```python
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
```

搭建好的效果：

![image-20230929001952983](https://cdn.jsdelivr.net/gh/SankHyan24/image1/img/image-20230929001952983.png)