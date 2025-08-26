import requests
import json
import os

url = "https://open.bigmodel.cn/api/paas/v4/files"
payload = {"purpose": "batch"}
headers = {
    "Authorization": "Bearer 73c95dbd36ed48bdbe79ead423219d4e.8pZApezlT8JLM4Rr",
    "Accept": "application/json"
}

try:
    # 检查文件是否存在
    if not os.path.exists('output.jsonl'):
        raise FileNotFoundError("output.jsonl 文件不存在")
    
    with open('output.jsonl', 'rb') as f:
        files = {
            "file": ("output.jsonl", f, "application/json-lines")  # 修改 content-type
        }
        response = requests.post(url, data=payload, files=files, headers=headers)
        
        # 打印详细错误信息
        if response.status_code != 200:
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            response.raise_for_status()
            
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
except FileNotFoundError as e:
    print(f"文件错误：{str(e)}")
except requests.exceptions.RequestException as e:
    print(f"请求错误：{str(e)}")
except Exception as e:
    print(f"其他错误：{str(e)}")