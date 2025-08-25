import os
import json
import requests
from zai import ZhipuAiClient
def generate_jsonl(image_urls, out_path):
    prompt = "请为这张图片生成正式风格的描述性英文标题"
    with open(out_path, "w", encoding="utf-8") as f:
        for i, url in enumerate(image_urls, start=1):
            record = {
                "custom_id": f"image_{i:03d}",
                "method": "POST",
                "path": "/v4/vision/chat/completions",
                "body": {
                    "model": "glm-4v-plus-0111",  # 修改为完整模型名称
                    "images": [url],
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "image_url", "image_url": {"url": url}},
                                {"type": "text", "text": prompt}
                            ]
                        }
                    ],
                    "thinking": {"type": "enabled"}
                }
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"已生成 {out_path}")
def validate_jsonl(file_path):
    """验证生成的 JSONL 文件格式"""
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                record = json.loads(line)
                # 验证模型名称
                if record["body"]["model"] != "glm-4v-plus-0111":
                    raise ValueError(f"行 {line_num}: 模型名称不正确")
                # 验证图片 URL
                images = record["body"]["images"]
                if not images or not images[0]:
                    raise ValueError(f"行 {line_num}: 图片 URL 为空")
                # 验证消息中的 URL
                msg_url = record["body"]["messages"][0]["content"][0]["image_url"]["url"]
                if not msg_url:
                    raise ValueError(f"行 {line_num}: 消息中 URL 为空")
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                raise ValueError(f"行 {line_num}: 格式错误 - {str(e)}")
    print("JSONL 文件验证通过")
def upload_file(file_path, api_key):
    url = "https://open.bigmodel.cn/api/paas/v4/files"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"purpose": "batch"}
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "application/json")}
        response = requests.post(url, headers=headers, files=files, data=data)
    print("上传响应：", response.text)
    response.raise_for_status()
    resp_json = response.json()
    file_id = resp_json.get("file_id") or resp_json.get("id") or resp_json.get("data", {}).get("id")
    if not file_id:
        raise ValueError(f"上传成功但未返回 file id，响应: {resp_json}")
    return file_id
def create_batch(file_id, api_key):
    client = ZhipuAiClient(api_key=api_key)
    create = client.batches.create(
        input_file_id=file_id,
        endpoint="/v4/vision/chat/completions",
        auto_delete_input_file=True,
        metadata={
            "description": "图片英文标题批处理"
        }
    )
    print("批处理任务创建成功：", create)
    return create
def main():
    image_urls = [
        "https://mpas.playinjoy.com/202508/b3dfdd2d-eef9-43f4-a447-8ba246c6612f.jpg",
        "https://mpas.playinjoy.com/202508/aa8f8523-dc1a-410d-a31b-e96f634ca4c9.jpg",
        "https://mpas.playinjoy.com/202508/16ed90f9-577a-4bfa-8269-513186481bc9.jpg",
        "https://mpas.playinjoy.com/202508/c00e1e22-83c5-4657-9199-86f95cf9f608.jpg",
    ]
    api_key = "0fb3b2fe955446ad8242430b14656cef.TPW91E6YZyJeH0dS"
    jsonl_file_path = "output.jsonl"
    generate_jsonl(image_urls, jsonl_file_path)
    validate_jsonl(jsonl_file_path)  # 添加验证步骤
    file_id = upload_file(jsonl_file_path, api_key)
    print("上传成功，file_id:", file_id)
    batch_info = create_batch(file_id, api_key)
    print("批处理任务信息：", batch_info)
if __name__ == "__main__":
    main()