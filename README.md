# GLM 批量图像描述生成器

这个项目使用智谱AI的GLM模型为图像生成描述。

## 配置

1. 复制 `.env.example` 文件并重命名为 `.env`:
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入你的智谱AI API密钥:
   ```
   ZHIPUAI_API_KEY=your_actual_api_key_here
   ```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

运行主程序:
```bash
python main.py
```

或者运行Web应用:
```bash
python app.py
```