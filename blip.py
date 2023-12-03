import requests

API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
blip_headers = {"Authorization": "Bearer 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"}

# 
def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    # #DEBUG
    # print("DEBUG: data type is:")
    # print(type(data)) # <class 'bytes'>
    response = requests.post(API_URL, headers=blip_headers, data=data)
    return response.json()

output = query("blip_test_fire.jpg")
# print(type(output))  # 这会打印出 output 的类型

generated_text = output[0]['generated_text']  # 取出列表的0号元素，然后用 ['generated_text'] 取出字典中的值
# print(type(generated_text))  # 这会打印出 generated_text 的类型 

print(generated_text)  # 打印取出的字符串值
