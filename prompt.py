import requests

url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

payload = {
    "model": "glm-4v-plus-0111",
    "do_sample": True,
    "stream": False,
    "thinking": { "type": "enabled" },
    "temperature": 0.6,
    "top_p": 0.95,
    "response_format": { "type": "text" },
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "image_url": { "url": "https://mpas.playinjoy.com/202508/16ed90f9-577a-4bfa-8269-513186481bc9.jpg" },
                    "type": "image_url"
                },
                {
                    "type": "text",
                    "text": "## 角色设定 (System Role): 你是一名专业的图像描述专家。你的任务是将图片内容转化为高质量的英文提示词，用于文本到图像的生成模型。 ## 任务说明 (User Instruction): 请仔细观察提供的图片，并生成一段详细、具体、富有创造性的英文短语，描述图片中的主体对象、场景、动作、光线、材质、色彩、构图和艺术风格。 ## 输出要求 (Output Requirements): **   **语言**： 严格使用英文。 **   **细节**： 尽可能多地描绘图片细节，包括但不限于物体、人物、背景、前景、纹理、表情、动作、服装、道具等。 **   **角度**： 尽可能从多个角度丰富描述，例如特写、广角、俯视、仰视等，但不要直接写“角度”。 **   **连接**： 使用逗号（,）连接不同的短语，形成一个连贯的提示词。 **   **人物**： 描绘人物时，使用第三人称（如 'a woman', 'the man'）。 **   **质量词**： 在生成的提示词末尾，务必添加以下质量增强词：`, best quality, high resolution, 4k, high quality`。 ## 只生成提示词，不需要描述过程及其他，并且一定要在质量词"
                }
            ]
        }
    ]
}
headers = {
    "Authorization": "Bearer 59856fbdedc949b993a04e2c057aa6fd.y1mbUzy6KYfhx5lK",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())