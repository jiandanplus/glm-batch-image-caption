import os
import json
import time
import requests
from zhipuai import ZhipuAI

# 配置信息
API_KEY = "0fb3b2fe955446ad8242430b14656cef.TPW91E6YZyJeH0dS"
IMAGE_URLS = [
    "https://mpas.playinjoy.com/202508/b3dfdd2d-eef9-43f4-a447-8ba246c6612f.jpg",
    "https://mpas.playinjoy.com/202508/aa8f8523-dc1a-410d-a31b-e96f634ca4c9.jpg",
    "https://mpas.playinjoy.com/202508/16ed90f9-577a-4bfa-8269-513186481bc9.jpg",
    "https://mpas.playinjoy.com/202508/c00e1e22-83c5-4657-9199-86f95cf9f608.jpg",
]
PROMPT = "Write a stable diffusion prompt for this image within 256 words."

def generate_jsonl(image_urls, out_path):
    """根据图片URL生成符合格式要求的jsonl文件"""
    with open(out_path, "w", encoding="utf-8") as f:
        for i, url in enumerate(image_urls, start=1):
            record = {
                "custom_id": f"image_{i:03d}",
                "method": "POST",
                "url": "/v4/chat/completions",
                "body": {
                    "model": "glm-4v-plus-0111",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "image_url", "image_url": {"url": url}},
                                {"type": "text", "text": PROMPT}
                            ]
                        }
                    ],
                    "thinking": {"type": "disabled"}
                }
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"已生成 {out_path}")

def upload_file(file_path, api_key):
    """上传.jsonl文件到glm，并返回input_file_id"""
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

def create_batch(input_file_id, api_key):
    """通过input_file_id创建glm批处理任务"""
    client = ZhipuAI(api_key=api_key)
    create = client.batches.create(
        input_file_id=input_file_id,
        endpoint="/v4/chat/completions",
        auto_delete_input_file=True,
        metadata={
            "description": "图片英文标题批处理"
        }
    )
    print("批处理任务创建成功：", create)
    return create.id

def check_batch_status(batch_id, api_key):
    """检查批处理任务状态"""
    client = ZhipuAI(api_key=api_key)
    batch_info = client.batches.retrieve(batch_id)
    return batch_info

def get_batch_result(output_file_id, api_key):
    """通过output_file_id获取处理结果"""
    client = ZhipuAI(api_key=api_key)
    content = client.files.content(output_file_id)
    # 使用write_to_file方法把返回结果写入文件
    result_file = "batch_result.jsonl"
    content.write_to_file(result_file)
    return result_file

def parse_batch_result(result_file):
    """解析返回结果中的request_id、content，并创建txt文件"""
    with open(result_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    data = json.loads(line)
                    request_id = data.get("custom_id", "")
                    content = data.get("response", {}).get("body", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    if request_id and content:
                        # 以request_id命名，创建txt文件，将对应的content写入txt文件中
                        txt_filename = f"{request_id}.txt"
                        with open(txt_filename, "w", encoding="utf-8") as txt_file:
                            txt_file.write(content)
                        print(f"已创建文件 {txt_filename}")
                except json.JSONDecodeError:
                    print(f"解析行失败: {line}")

def calculate_duration(created_at, completed_at):
    """根据created_at和completed_at之间的时间段，计算任务用时"""
    if completed_at and created_at:
        # 时间戳是毫秒单位，需要除以1000转换为秒
        duration_seconds = (completed_at - created_at) / 1000
        duration_minutes = duration_seconds / 60
        print(f"任务总耗时: {duration_seconds} 秒 ({duration_minutes:.2f} 分钟)")
        return duration_seconds
    else:
        print("任务时间信息不完整")
        return None

def main():
    # 1. 根据提供的example.jsonl文件生成符合格式要求的jsonl文件
    jsonl_file_path = "batch_input.jsonl"
    generate_jsonl(IMAGE_URLS, jsonl_file_path)
    
    # 2. 上传.jsonl文件到glm，并返回input_file_id
    file_id = upload_file(jsonl_file_path, API_KEY)
    print("上传成功，file_id:", file_id)
    
    # 3. 通过返回的input_file_id创建glm批处理任务，返回status、input_file_id、output_file_id、created_at、completed_at
    batch_id = create_batch(file_id, API_KEY)
    
    # 轮询检查任务状态直到完成
    output_file_id = None
    created_at = None
    completed_at = None
    
    while True:
        batch_info = check_batch_status(batch_id, API_KEY)
        print(f"批处理任务状态: {batch_info.status}")
        
        if batch_info.status == "completed":
            output_file_id = batch_info.output_file_id
            created_at = batch_info.created_at
            completed_at = batch_info.completed_at
            print(f"任务完成，output_file_id: {output_file_id}")
            break
        elif batch_info.status in ["failed", "cancelled"]:
            print(f"任务失败或已取消，状态: {batch_info.status}")
            return
        else:
            print("任务仍在处理中...")
            time.sleep(10)  # 每10秒检查一次状态
    
    # 4. 根据created_at和completed_at之间的时间段，计算任务用时
    duration = calculate_duration(created_at, completed_at)
    
    # 5. 通过output_file_id获取处理结果
    result_file = get_batch_result(output_file_id, API_KEY)
    print(f"结果已保存到 {result_file}")
    
    # 6. 提取返回结果中的request_id、content，并以request_id命名创建txt文件
    parse_batch_result(result_file)

if __name__ == "__main__":
    main()