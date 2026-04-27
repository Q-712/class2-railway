# -*- coding: utf-8 -*-
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# 配置阿里云百炼
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_CHAT_MODEL = "qwen-plus"

# 读取 API Key
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise RuntimeError("没有读取到环境变量 DASHSCOPE_API_KEY")

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=api_key,
    base_url=QWEN_BASE_URL,
)

# 创建 FastAPI 应用
app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 定义请求体格式
class ChatRequest(BaseModel):
    message: str


# 定义聊天接口
@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message
    print(f"收到消息: {user_message}")  # 调试用

    try:
        completion = client.chat.completions.create(
            model=QWEN_CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个友好的AI助手，回答要准确、简洁、有帮助。",
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=0.7,
        )

        answer = completion.choices[0].message.content
        print(f"返回回答: {answer[:50]}...")  # 调试用
        return {"response": answer}

    except Exception as e:
        print(f"错误: {e}")  # 调试用
        return {"response": f"出错了：{str(e)}"}


# 健康检查接口
@app.get("/health")
async def health():
    return {"status": "ok"}


# ⚠️ 重要：静态文件挂载必须放在最后！！！
app.mount("/", StaticFiles(directory="static", html=True), name="static")