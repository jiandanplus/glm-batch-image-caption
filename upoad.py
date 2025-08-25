import requests

url = "https://open.bigmodel.cn/api/paas/v4/files"

payload = { "purpose": "batch" }
headers = {"Authorization": "Bearer 73c95dbd36ed48bdbe79ead423219d4e.8pZApezlT8JLM4Rr"}

with open('output.jsonl', 'rb') as f:
    files = { "file": ("output.jsonl", f, "application/jsonl") }
    response = requests.post(url, data=payload, files=files, headers=headers)
    print(response.text)