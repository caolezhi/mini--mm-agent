# 从 0 到 1 手写一个 Mini AI Agent

> 面向初学者：从 **Python + FastAPI** 开始，一步步写到 **Responses API、上下文、SQLite、流式输出、Tool Calling、Agent Loop、E2B Sandbox 和最小网页前端**。

这不是一个“把最终代码复制下来就结束”的 Demo。

这份仓库更像一本很小的实战教材：我们会从最简单的 `print()` 开始，每次只增加一个新概念，并解释：

- 为什么现在需要它？
- 它解决了什么问题？
- 核心代码到底是什么意思？
- 如果删掉它会发生什么？
- 正常运行后应该看到什么？
- 常见错误怎么排查？

**本项目不涉及数学建模。** 它实现的是一个通用、简化、适合学习原理的 AI Agent。

> 本教程统一使用 **Responses API**。如果你使用第三方 OpenAI-compatible API，请先确认供应商确实支持 Responses API；只兼容部分 OpenAI 接口，不代表一定兼容 `/responses`。

---

## 最终你会做出什么？

![Mini AI Agent 工作流程](docs/images/agent-workflow.svg)

学完后，你会亲手搭出下面这条完整链路：

```text
用户在浏览器输入任务
        ↓
JavaScript 发送 POST /agent
        ↓
FastAPI 接收 JSON 请求
        ↓
Agent Service 调用 Responses API
        ↓
模型判断是否需要工具
   ┌────┴────┐
   │         │
不需要      需要
   │         ↓
直接回答   function_call
             ↓
         Tool Registry
             ↓
       真正执行 Python 函数
             ↓
         工具真实结果
             ↓
     function_call_output
             ↓
        再交给模型
             ↓
      Agent Loop 继续
             ↓
          最终回答
             ↓
        返回浏览器
```

这里最重要的一句话是：

> **LLM 负责判断和选择动作；你的 Python 程序负责真正执行动作。**

---

## 适合谁？

如果你有下面这些感受，这份教程就是为你准备的：

- 会一点 Python，但没写过完整后端；
- 知道大模型 API，却不知道一个 Agent 项目到底怎么组织；
- 一看到 `async/await`、FastAPI、数据库、Tool Calling 就觉得东西太多；
- 能运行别人项目，但不知道如果让自己从空文件夹开始该怎么写；
- 想先搞懂 Agent 的底层逻辑，再学习 LangGraph、LangChain 或更大的开源项目。

你不需要预先掌握 Agent 框架。

我们甚至**故意不使用 Agent 框架**，因为这里的目标是看见它最核心的骨架。

---

## 最终项目结构

```text
mini--mm-agent/
├── .env.example
├── .gitignore
├── requirements.txt
├── main.py
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── llm.py
│   ├── tools.py
│   ├── sandbox.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── response_service.py
│       └── agent_service.py
│
├── frontend/
│   └── index.html
│
└── docs/
    ├── SCREENSHOTS.md
    └── images/
```

注意：仓库中放的是**最终版本代码**。学习时建议仍然按照下面的章节一步一步写，不要一开始就把所有最终代码复制过去。

---

## 20 章学习路线

| 阶段 | 章节 | 最终获得的能力 |
| --- | --- | --- |
| 环境与 Python | 1–3 | WSL、VSCode、虚拟环境、运行 Python |
| Web 基础 | 4–6 | FastAPI、GET/POST、JSON、`.env` |
| LLM 应用 | 7–11 | Responses API、多轮状态、SQLite、Reset |
| 工程化 | 12–14 | 分层、async/await、日志、SSE 流式输出 |
| Agent 核心 | 15–18 | Function Tool、Tool Registry、Agent Loop |
| 安全执行与产品串联 | 19–20 | E2B Sandbox、网页前端、完整 Agent |

---

# 第 1 章：Windows + WSL + VSCode

> **本章目标**：让 Windows 上的 VSCode 真正连接到 WSL Ubuntu。  
> **完成效果**：VSCode 左下角出现 `WSL: Ubuntu`，终端路径位于 `/home/...`。  
> **核心知识**：WSL、Linux 文件系统、远程开发。

## 为什么这样配置？

你可以把现在的开发环境理解成：

```text
Windows
└── VSCode 图形界面
      ↓ 连接
WSL Ubuntu
├── 项目文件
├── Python
├── Git
└── Terminal
```

这样做的好处是，后面 FastAPI、Shell、Python、数据库和部署环境都更接近真实 Linux 服务器。

## 操作

在 Windows 的 VSCode 安装微软官方扩展：

```text
WSL
Python
Pylance
```

然后按：

```text
Ctrl + Shift + P
```

搜索：

```text
WSL: Connect to WSL
```

选择 Ubuntu。

打开新的 VSCode Terminal：

```bash
pwd
python3 --version
```

`pwd` 应该类似：

```text
/home/yourname
```

如果看到的是 `C:\...`，说明你现在还是 Windows 终端，不是 WSL Terminal。

## 本章检查

你应该能解释：

> VSCode 界面可以运行在 Windows，但当前项目和 Python 实际运行在 WSL Ubuntu 中。

---

# 第 2 章：创建项目与 Python 虚拟环境

> **本章目标**：给项目创建独立 Python 环境。  
> **完成效果**：终端前出现 `(.venv)`，`which python` 指向当前项目。  
> **核心知识**：venv、依赖隔离、Python Interpreter。

创建项目：

```bash
mkdir mini--mm-agent
cd mini--mm-agent
```

创建虚拟环境：

```bash
python3 -m venv .venv
```

激活：

```bash
source .venv/bin/activate
```

确认：

```bash
which python
```

应该类似：

```text
/home/yourname/mini--mm-agent/.venv/bin/python
```

### 为什么每个项目都可以叫 `.venv`？

因为真正路径不同：

```text
/home/you/project-a/.venv
/home/you/project-b/.venv
```

所以互不影响。

在 VSCode 中按：

```text
Ctrl + Shift + P
→ Python: Select Interpreter
→ ./.venv/bin/python
```

### 如果搜不到 `Python: Select Interpreter`

先确认：

1. Microsoft Python 扩展已经安装；
2. 它是安装并启用在 WSL 环境，而不只是 Windows；
3. 必要时执行 `Developer: Reload Window`。

---

# 第 3 章：先运行最普通的 Python

> **本章目标**：验证 VSCode → WSL → `.venv` → Python 整条链路。  
> **完成效果**：终端输出 `Hello Mini Agent`。  
> **核心知识**：Python 文件、运行程序、逐层验证。

创建：

```text
app/main.py
```

先只写：

```python
print("Hello Mini Agent")
```

运行：

```bash
python app/main.py
```

得到：

```text
Hello Mini Agent
```

为什么要先做这么简单的东西？

因为一个 Agent 项目有很多层。以后报错时，你应该学会逐层判断：

```text
Python 能不能运行？
↓
FastAPI 能不能运行？
↓
HTTP 请求有没有收到？
↓
模型 API 有没有打通？
↓
工具有没有执行？
↓
Agent Loop 有没有继续？
```

**逐层验证**是比背代码更重要的开发习惯。

---

# 第 4 章：第一次启动 FastAPI

> **本章目标**：把 Python 程序变成一个 Web 服务。  
> **完成效果**：浏览器访问 `127.0.0.1:8001` 能看到 JSON。  
> **核心知识**：FastAPI、Uvicorn、Route。

安装：

```bash
pip install fastapi uvicorn
```

把 `app/main.py` 改成：

```python
from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Hello Mini Agent"
    }
```

启动：

```bash
uvicorn app.main:app --reload --port 8001
```

打开：

```text
http://127.0.0.1:8001
```

应该看到：

```json
{"message":"Hello Mini Agent"}
```

再打开：

```text
http://127.0.0.1:8001/docs
```

这是 FastAPI 自动生成的 Swagger API 文档。

## `app = FastAPI()` 是什么？

可以先把它理解成：

> 创建一个后端应用对象。

## `@app.get("/")` 是什么？

它告诉 FastAPI：

> 当有人用 GET 访问 `/` 时，执行下面的 `home()`。

## `uvicorn app.main:app` 怎么读？

```text
uvicorn
→ 用 Uvicorn 运行 Web 服务

app.main
→ 找 app/main.py

:app
→ 找这个文件中的 app = FastAPI()
```

### 常见错误：Address already in use

```text
[Errno 98] Address already in use
```

说明端口已被其他进程占用。

查看：

```bash
ss -ltnp | grep :8001
```

或者临时换端口。

---

# 第 5 章：GET、POST、Header 和 JSON

> **本章目标**：理解前端到底怎样把一句话交给后端。  
> **完成效果**：能用 Swagger 或 curl 发送 POST JSON。  
> **核心知识**：HTTP Method、Header、Body、JSON。

这是整个教程里非常值得认真理解的一章。

浏览器地址栏输入网址时，默认发送的是：

```text
GET /
```

GET 通常表示“读取”。

但聊天/Agent 请求要把数据交给服务器，例如：

```json
{
  "input": "你好"
}
```

于是更适合 POST。

创建请求数据模型：

```python
from pydantic import BaseModel


class ResponseRequest(BaseModel):
    input: str
```

接口：

```python
@app.post("/responses")
def create_response(request: ResponseRequest):
    return {
        "output": f"你输入了：{request.input}"
    }
```

如果你直接在浏览器地址栏打开 `/responses`，可能看到：

```json
{"detail":"Method Not Allowed"}
```

这并不是接口不存在，而是：

```text
浏览器地址栏发送 GET
但接口要求 POST
```

用 curl：

```bash
curl -X POST http://127.0.0.1:8001/responses \
  -H "Content-Type: application/json" \
  -d '{"input":"你好"}'
```

拆开理解：

```text
-X POST
→ 请求方法

-H "Content-Type: application/json"
→ Header，告诉服务器 Body 是 JSON

-d '{"input":"你好"}'
→ Body，真正提交的数据
```

以后前端的 `fetch()` 本质上做的也是这一件事。

### 常见错误

```bash
curl -x POST ...
```

小写 `-x` 是代理设置，所以会出现：

```text
Could not resolve proxy: POST
```

正确是大写：

```bash
-X POST
```

---

# 第 6 章：`.env` —— 不要把 API Key 写进代码

> **本章目标**：把密钥和源码分开。  
> **完成效果**：程序能从 `.env` 读取配置，GitHub 不包含真实 Key。  
> **核心知识**：环境变量、dotenv、`.gitignore`。

安装：

```bash
pip install python-dotenv
```

创建本地 `.env`：

```env
API_KEY=你的真实API_KEY
BASE_URL=你的API地址
MODEL_NAME=你的模型名
E2B_API_KEY=你的E2B_KEY
```

**不要把真实 `.env` 提交到 GitHub。**

仓库里提供的是 `.env.example`：

```env
API_KEY=
BASE_URL=https://api.openai.com/v1
MODEL_NAME=your-responses-compatible-model
E2B_API_KEY=
```

`app/config.py`：

```python
import os

from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
E2B_API_KEY = os.getenv("E2B_API_KEY")
```

这里：

```python
load_dotenv()
```

负责读取 `.env`。

而：

```python
os.getenv("MODEL_NAME")
```

负责取某一个环境变量。

### `.env` 里的字符串要不要引号？

通常：

```env
MODEL_NAME=my-model
```

就可以。

如果值中有空格或特殊字符，也可以：

```env
PROJECT_NAME="My Agent"
```

不要使用中文弯引号 `“ ”`。

---

# 第 7 章：第一次调用 Responses API

> **本章目标**：暂时不做 Agent，先把 Python → 大模型打通。  
> **完成效果**：终端能打印真实模型回答。  
> **核心知识**：OpenAI SDK、Responses API、`input`、`instructions`、`output_text`。

安装：

```bash
pip install openai
```

先写最小测试：

```python
from openai import OpenAI

from app.config import API_KEY, BASE_URL, MODEL_NAME


client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

response = client.responses.create(
    model=MODEL_NAME,
    instructions="你是一个简洁的AI助手。",
    input="你好，请只回答：连接成功",
)

print(response.output_text)
```

如果看到：

```text
连接成功
```

就说明：

```text
Python
↓
SDK
↓
Responses API
↓
模型
↓
回答
```

已经打通。

## 为什么读取 `response.output_text`？

Responses API 的 `output` 不一定只有普通文字，它还可能包含诸如工具调用等不同 output item。

所以 SDK 提供：

```python
response.output_text
```

用于方便地取得聚合后的文本输出。

### 第三方 API 注意

如果你的 `BASE_URL` 指向第三方供应商，必须确认它真的支持 Responses API。

有些服务虽然写着“OpenAI-compatible”，却只兼容一部分接口。

---

# 第 8 章：把模型接进自己的 FastAPI

> **本章目标**：让 `POST /responses` 真正调用模型。  
> **完成效果**：Swagger 里发一句话，返回模型真实回答。  
> **核心知识**：API 层、LLM Gateway、异步网络调用。

![一次请求是如何流动的](docs/images/request-flow.svg)

从这一章开始，请经常回来看这张图。

请求开始形成真正的调用链：

```text
客户端
↓
FastAPI
↓
Service
↓
LLM Gateway
↓
Responses API
```

最终项目把 SDK 封装在 `app/llm.py`：

```python
from openai import AsyncOpenAI

from app.config import API_KEY, BASE_URL, MODEL_NAME


client = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)


async def create_model_response(
    input_data,
    *,
    instructions: str,
    previous_response_id: str | None = None,
    tools=None,
):
    kwargs = {
        "model": MODEL_NAME,
        "instructions": instructions,
        "input": input_data,
    }

    if previous_response_id:
        kwargs["previous_response_id"] = previous_response_id

    if tools:
        kwargs["tools"] = tools

    return await client.responses.create(**kwargs)
```

## 为什么专门写 `llm.py`？

如果路由里到处写 SDK 调用，那么以后换 API 地址、模型供应商、公共配置会非常乱。

我们把它当作一个小型 **LLM Gateway**：

```text
项目其他代码
只知道 create_model_response()
        ↓
llm.py
才知道具体 SDK 和 BASE_URL
```

---

# 第 9 章：多轮对话与 `previous_response_id`

> **本章目标**：让模型知道上一轮发生了什么。  
> **完成效果**：先说“我叫小明”，下一轮问名字时能回答。  
> **核心知识**：Response ID、会话状态、上下文链。

第一次请求：

```python
response1 = await client.responses.create(
    model=MODEL_NAME,
    instructions="你是AI助手",
    input="我叫小明",
)
```

得到：

```python
response1.id
```

下一轮：

```python
response2 = await client.responses.create(
    model=MODEL_NAME,
    instructions="你是AI助手",
    input="我叫什么？",
    previous_response_id=response1.id,
)
```

可以把它理解成：

```text
Response 1
↓
response1.id
↓
Response 2.previous_response_id
```

但服务器还需要解决另一个问题：

```text
user-a 上一次 response_id 是什么？
user-b 上一次 response_id 又是什么？
```

这就是为什么下一章需要 session 和数据库。

---

# 第 10 章：SQLite 保存 Session 与消息

> **本章目标**：让服务器重启后仍然保留会话映射。  
> **完成效果**：重启 Uvicorn 后，同一个 `session_id` 仍可继续。  
> **核心知识**：SQLite、表、SELECT、INSERT、DELETE。

我们使用 SQLite，因为它非常适合教学：

```text
不需要单独启动数据库服务器
一个 chat.db 文件就是数据库
```

项目保存两张表：

```text
messages
→ 本地聊天历史

sessions
→ session_id 对应最新 previous_response_id
```

核心 SQL：

```sql
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    previous_response_id TEXT
)
```

例如：

```text
browser-a → resp_123
browser-b → resp_999
```

下一次 browser-a 请求时：

```python
previous_response_id = get_previous_response_id(session_id)
```

再传给模型。

## 为什么还要保存 messages？

`previous_response_id` 主要负责**模型侧上下文连接**。

而本地 `messages` 以后可以用于：

- 展示聊天历史；
- 调试；
- 审计；
- 换供应商后迁移数据。

### 直接查看 SQLite

Ubuntu 安装：

```bash
sudo apt install sqlite3
```

在项目目录：

```bash
sqlite3 chat.db
```

然后：

```sql
.tables
SELECT * FROM messages;
.quit
```

如果出现：

```text
no such table: messages
```

先运行：

```bash
pwd
```

确认你打开的是**项目目录中的 `chat.db`**，而不是在 `~` 下误创建了一个新的空数据库。

---

# 第 11 章：Reset —— 开始一段新会话

> **本章目标**：允许用户主动清掉旧上下文。  
> **完成效果**：调用 `/responses/reset` 后旧会话不再继续。  
> **核心知识**：状态清理、Session 生命周期。

Reset 的逻辑很朴素：

```text
删除这个 session 的 messages
+
删除这个 session 的 previous_response_id
```

项目中的：

```python
def clear_session(session_id: str):
    ...
```

就是做这件事。

所以“会话重置”并不神秘，本质上只是清掉服务器保存的状态。

---

# 第 12 章：把代码拆开 —— 从能跑到能维护

> **本章目标**：理解为什么真实项目会有很多文件夹。  
> **完成效果**：能说出 `routes.py / services / llm.py / db.py / tools.py` 各自负责什么。  
> **核心知识**：职责分离、项目分层、Service、Gateway。

![Mini Agent 项目结构](docs/images/project-structure.svg)

如果所有代码都写进 `main.py`，很快会变成：

```text
main.py
├── API
├── 数据库
├── 模型
├── Tools
├── Agent Loop
├── 日志
└── 几百行代码
```

所以我们拆成：

```text
app/main.py
→ 组装 FastAPI

app/api/routes.py
→ HTTP 接口

app/services/response_service.py
→ 普通模型业务

app/services/agent_service.py
→ Tool Executor + Agent Loop

app/llm.py
→ Responses API Gateway

app/db.py
→ SQLite

app/tools.py
→ Tool 定义和注册

app/sandbox.py
→ E2B 代码执行
```

以后看到大型项目的：

```text
api/
services/
infra/
domain/
```

不要先被目录数量吓到。

先问：

> **这一层的职责是什么？**

---

# 第 13 章：`async / await`、异常处理和日志

> **本章目标**：让项目开始具备真正后端的工程能力。  
> **完成效果**：模型 API 使用异步调用，错误有日志可查。  
> **核心知识**：异步 I/O、Exception、Logging。

模型 API 是网络请求。

等待网络时，CPU 并不需要一直占着执行机会。

于是：

```python
async def create_response(...):
    response = await client.responses.create(...)
```

可以先简单理解：

```text
async def
→ 这是一个支持异步等待的函数

await
→ 等结果时允许事件循环处理别的任务
```

API 层可以：

```python
try:
    ...
except Exception:
    logger.exception("模型调用失败")
    raise HTTPException(
        status_code=500,
        detail="模型调用失败",
    )
```

用户看到简洁错误：

```json
{"detail":"模型调用失败"}
```

开发者终端则能看到完整 Traceback。

## 为什么不用全部 `print()`？

Logging 有等级：

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Agent 中尤其适合记录：

```python
logger.info("Agent step=%s", step + 1)
logger.info("执行工具 name=%s arguments=%s", name, arguments)
logger.exception("工具执行失败")
```

不要记录 API Key。

---

# 第 14 章：流式输出 —— 为什么回答可以一点点出现

> **本章目标**：实现 Responses API Streaming + SSE。  
> **完成效果**：终端/前端能一块一块收到模型文本。  
> **核心知识**：stream、event、`response.output_text.delta`、SSE、`yield`。

普通请求：

```text
模型全部生成完成
↓
一次性返回
```

流式请求：

```text
生成一点
↓
马上返回一点
↓
再生成一点
↓
再返回一点
```

Responses API：

```python
stream = await client.responses.create(
    model=MODEL_NAME,
    input=user_input,
    stream=True,
)
```

读取文本增量：

```python
async for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta)
```

FastAPI 还需要把这些增量继续转发给浏览器：

```python
return StreamingResponse(
    event_generator(),
    media_type="text/event-stream",
)
```

SSE 数据大概长这样：

```text
data: {"delta":"AI"}

data: {"delta":" Agent"}

data: [DONE]
```

### `yield` 和 `return` 的区别

粗略理解：

```text
return
→ 给一次结果，然后函数结束

yield
→ 先给一块结果，函数以后还能继续产出
```

curl 测试流式时使用：

```bash
curl -N -X POST http://127.0.0.1:8001/responses/stream \
  -H "Content-Type: application/json" \
  -d '{"session_id":"stream-test","input":"解释AI Agent"}'
```

`-N` 告诉 curl 不要缓冲输出。

---

# 第 15 章：Tool Calling —— Chatbot 与 Agent 的分界线

> **本章目标**：让模型可以提出“调用函数”的请求。  
> **完成效果**：模型能够产生 `function_call`。  
> **核心知识**：Function Tool、JSON Schema、模型决策与程序执行的区别。

![Agent 为什么会调用工具](docs/images/tool-calling-loop.svg)

先写一个最普通的 Python 函数：

```python
def add_numbers(a: float, b: float):
    return a + b
```

注意：到这里它还只是 Python 函数。

为了让模型知道这个函数存在，我们还需要一份“说明书”：

```python
{
    "type": "function",
    "name": "add_numbers",
    "description": "计算两个数字的加法",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"}
        },
        "required": ["a", "b"],
        "additionalProperties": False
    },
    "strict": True
}
```

这份 Tool Definition 是：

```text
给模型看的工具说明书
```

而：

```python
def add_numbers(...):
```

才是：

```text
真正能执行的 Python 能力
```

## 最关键的理解

LLM **不会直接进入你的 Python 进程执行函数**。

模型只会返回类似：

```text
type = function_call
name = add_numbers
arguments = {"a":123,"b":456}
```

然后你的代码看到这个请求以后，再真正调用：

```python
add_numbers(a=123, b=456)
```

所以：

> **Tool Calling = 模型提出动作；Tool Executor = 程序执行动作。**

---

# 第 16 章：Tool Registry —— 怎么管理很多工具

> **本章目标**：避免不断写 `if / elif`。  
> **完成效果**：根据模型返回的工具名自动找到 Python 函数。  
> **核心知识**：Registry、`json.loads()`、`**kwargs`。

如果工具越来越多，这种代码很快会变丑：

```python
if name == "get_server_time":
    ...
elif name == "add_numbers":
    ...
elif name == "run_python":
    ...
```

所以项目使用字典：

```python
TOOL_REGISTRY = {
    "get_server_time": get_server_time,
    "add_numbers": add_numbers,
    "run_python": run_python,
}
```

模型返回：

```text
name = add_numbers
```

程序：

```python
tool_function = TOOL_REGISTRY.get(tool_name)
```

就能找到函数。

模型返回的 arguments 通常是 JSON 字符串：

```python
'{"a":123,"b":456}'
```

所以：

```python
tool_arguments = json.loads(tool_call.arguments)
```

变成 Python 字典：

```python
{
    "a": 123,
    "b": 456,
}
```

然后：

```python
tool_function(**tool_arguments)
```

等价于：

```python
add_numbers(a=123, b=456)
```

### `json.dumps` 和 `json.loads`

非常容易混：

```text
json.dumps
Python 对象 → JSON 字符串

json.loads
JSON 字符串 → Python 对象
```

---

# 第 17 章：把真实工具结果交回模型

> **本章目标**：完成“模型请求工具 → 程序执行 → 结果回模型”。  
> **完成效果**：模型能基于真实工具结果继续回答。  
> **核心知识**：`function_call_output`、`call_id`。

Responses API 返回的 `response.output` 中可能有：

```python
item.type == "function_call"
```

我们找到这些调用：

```python
tool_calls = [
    item
    for item in response.output
    if item.type == "function_call"
]
```

执行以后构造：

```python
{
    "type": "function_call_output",
    "call_id": tool_call.call_id,
    "output": str(tool_result),
}
```

## 为什么要 `call_id`？

模型可能一次提出多个调用。

`call_id` 告诉模型：

> 这一个结果对应你刚才的哪一次 function call。

然后再次调用模型：

```python
response = await create_model_response(
    tool_outputs,
    previous_response_id=response.id,
    tools=TOOL_DEFINITIONS,
)
```

于是模型现在拥有了真实的工具结果。

---

# 第 18 章：Agent Loop —— 整个 Agent 的心脏

> **本章目标**：让模型可以连续做多步，而不是调用一次工具就强制结束。  
> **完成效果**：Agent 可以“模型 → 工具 → 模型 → 工具 → 最终回答”。  
> **核心知识**：循环、观察工具结果、停止条件。

最小 Agent Loop 可以浓缩成：

```python
response = await create_model_response(...)

for step in range(max_steps):
    tool_calls = [
        item
        for item in response.output
        if item.type == "function_call"
    ]

    if not tool_calls:
        return response.output_text

    tool_outputs = []

    for tool_call in tool_calls:
        result = await execute_tool(tool_call)

        tool_outputs.append({
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": str(result),
        })

    response = await create_model_response(
        tool_outputs,
        previous_response_id=response.id,
        tools=TOOL_DEFINITIONS,
    )
```

翻译成人话：

```text
让模型判断下一步
↓
有工具请求吗？
├─ 没有 → 返回最终答案
└─ 有
    ↓
  执行工具
    ↓
  把真实结果交回模型
    ↓
  模型再次判断
    ↓
  回到循环
```

这就是 Agent 最核心的运行机制之一。

## 为什么必须有 `max_steps`？

千万不要无脑：

```python
while True:
```

模型可能因为错误不断调用工具。

所以 Agent 要有停止边界，例如：

```text
最大步骤数
最大执行时间
最大 Token
最大成本
```

本项目先用：

```python
max_steps = 10
```

---

# 第 19 章：E2B Sandbox —— 不要在自己机器上 `exec()` 模型代码

> **本章目标**：安全地执行模型生成的 Python。  
> **完成效果**：Agent 可以调用 `run_python(code)`，代码运行在 E2B 隔离环境。  
> **核心知识**：Sandbox、安全边界、通用代码执行工具。

我们希望 Agent 拥有一个很通用的能力：

```text
run_python(code)
```

例如用户说：

```text
请用 Python 计算 1 到 10000 所有整数的平方和
```

模型自己生成：

```python
print(sum(i ** 2 for i in range(1, 10001)))
```

然后交给工具执行。

## 为什么不能直接：

```python
exec(model_generated_code)
```

因为那意味着模型生成的代码直接运行在你的真实 WSL / 服务器中。

理论上它可能：

```text
读取 .env
访问文件
删除项目
执行危险系统命令
```

所以代码执行应该有安全边界。

安装：

```bash
pip install e2b-code-interpreter
```

`.env`：

```env
E2B_API_KEY=你的Key
```

项目中的 `app/sandbox.py`：

```python
from e2b_code_interpreter import Sandbox


def run_python(code: str):
    with Sandbox.create() as sandbox:
        execution = sandbox.run_code(code)

        if execution.error:
            return f"Python执行失败：{execution.error}"

        if execution.logs.stdout:
            return "\n".join(execution.logs.stdout)

        if execution.text:
            return execution.text

        return "代码执行成功，但没有输出。"
```

### 为什么 `execution.text` 有时是 `None`？

如果代码：

```python
print(123 + 456)
```

输出属于 stdout，所以看：

```python
execution.logs.stdout
```

如果代码最后是表达式：

```python
123 + 456
```

则可能从：

```python
execution.text
```

拿到结果。

### 为什么 `Sandbox()` 报构造错误？

当前代码使用：

```python
Sandbox.create()
```

而不是直接手工构造底层 Sandbox 对象。

---

# 第 20 章：加一个最小网页，把整个 Agent 串起来

> **本章目标**：把后端变成真正能在浏览器使用的小产品。  
> **完成效果**：网页输入任务，Agent 调工具后把最终答案显示回来。  
> **核心知识**：HTML、JavaScript、fetch、CORS、session_id、端到端调用链。

我们故意先不用 React / Next.js。

因为这个教程的重点是 Agent，而不是前端框架。

最小前端只需要：

```text
HTML
CSS
JavaScript
fetch()
```

![Mini Agent 最小前端示意](docs/images/final-ui-example.svg)

前端最核心的是：

```javascript
const response = await fetch(
    "http://127.0.0.1:8001/agent",
    {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            session_id: sessionId,
            input: message
        })
    }
);
```

现在你应该能发现，它和第 5 章的 curl 是同一回事：

```text
curl
和
fetch()
```

都只是 HTTP 客户端。

## 为什么需要 `session_id`？

如果没有 session：

```text
浏览器 A
浏览器 B
```

服务器不知道各自应该接哪一条上下文。

本项目第一次打开网页时：

```javascript
crypto.randomUUID()
```

生成 session id，再放到：

```javascript
localStorage
```

所以刷新页面仍可以复用同一 session。

## CORS 又是什么？

前端：

```text
http://127.0.0.1:3000
```

后端：

```text
http://127.0.0.1:8001
```

端口不同，因此浏览器把它们视为不同 Origin。

所以 FastAPI 中配置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

# 最终运行

## 1. 克隆并进入仓库

```bash
git clone https://github.com/caolezhi/mini--mm-agent.git
cd mini--mm-agent
```

## 2. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`：

```env
API_KEY=...
BASE_URL=...
MODEL_NAME=...
E2B_API_KEY=...
```

## 5. 启动后端

推荐：

```bash
uvicorn app.main:app --reload --port 8001
```

或者：

```bash
python main.py
```

Swagger：

```text
http://127.0.0.1:8001/docs
```

你应该看到：

```text
GET  /
POST /responses
POST /responses/stream
POST /responses/reset
POST /agent
```

## 6. 启动前端

新开一个 Terminal：

```bash
python3 -m http.server 3000 --directory frontend
```

浏览器：

```text
http://127.0.0.1:3000
```

测试：

```text
请使用 Python 工具计算 1 到 10000 所有整数的平方和
```

后端理想日志：

```text
Agent step=1
执行工具 name=run_python arguments={...}
工具执行完成 name=run_python result=333383335000
Agent step=2
```

这时候整个系统就是：

```text
Browser
↓
FastAPI
↓
Agent Loop
↓
Responses API
↓
function_call
↓
Tool Registry
↓
run_python
↓
E2B Sandbox
↓
真实结果
↓
function_call_output
↓
Responses API
↓
最终回答
↓
Browser
```

---

# 这个项目中最重要的 8 个概念

## 1. FastAPI

负责把 HTTP 请求映射成 Python 函数。

## 2. Responses API

负责让模型处理输入、产生文本或提出 function call。

## 3. Session State

负责知道当前请求属于哪一段连续上下文。

## 4. SQLite

负责把本地消息、session 与 previous response id 持久化。

## 5. Tool Definition

给模型看的“工具说明书”。

## 6. Tool Registry / Executor

真正把工具名变成 Python 函数并执行。

## 7. Agent Loop

不断执行：

```text
模型判断
→ 工具
→ 结果
→ 模型再判断
```

直到完成。

## 8. Sandbox

让模型生成的代码与真实服务器尽量隔离。

---

# 常见报错与排错思路

## `Address already in use`

```bash
ss -ltnp | grep :8001
```

## `Method Not Allowed`

通常是你在地址栏直接打开了一个 POST 接口。

用 Swagger、curl 或前端 `fetch()`。

## Python 好像还在执行旧代码

看看 VSCode 标签页右边有没有未保存的小圆点。

```text
Ctrl + S
```

## SQLite `no such table`

先：

```bash
pwd
```

确认当前目录。

## `logger.info()` 为什么没显示？

如果你直接用：

```bash
python -c "..."
```

可能没有加载 `app/main.py` 中的 logging 配置。

测试时可临时：

```python
logging.basicConfig(level=logging.INFO)
```

## Tool 的 arguments 为什么是 `{}`？

检查 Tool Schema：

```text
properties
required
```

特别注意不要把：

```text
properties
```

拼成：

```text
proerties
```

并确认 `required` 在 `parameters` 内部。

## E2B 返回 `execution.text = None`

如果模型代码用了 `print()`，先看：

```python
execution.logs.stdout
```

---

# 如何判断你是真的“学会”，而不是“跑起来”了？

运行成功只是第一层。

## Level 1：你能解释

不看源码回答：

1. GET 和 POST 有什么区别？
2. `previous_response_id` 是干什么的？
3. Tool Definition 和 Python 函数有什么区别？
4. LLM 有没有真正执行工具？
5. `function_call_output` 是干什么的？
6. Agent Loop 为什么必须设置 `max_steps`？
7. 为什么模型生成的代码不应该直接 `exec()`？

## Level 2：你能闭卷重写

关掉本教程，新建一个空目录，自己重新写：

```text
FastAPI
Responses API
Session
SQLite
一个 Tool
Tool Registry
Agent Loop
```

卡住了再回来查。

## Level 3：你能改需求

尝试独立增加：

```text
multiply(a, b)
read_text_file(path)
created_at 字段
Agent 超时
最大 Tool 调用次数
```

## Level 4：你能设计一个新项目

例如：

```text
文件分析 Agent
代码审查 Agent
科研文献 Agent
数据分析 Agent
```

重点已经不是“复制这个仓库”，而是自己回答：

```text
Router 应该有哪些？
Service 怎么拆？
状态放哪里？
需要哪些 Tools？
哪些操作必须 Sandbox？
Agent 的停止条件是什么？
```

做到这里，才是真正开始具备独立开发类似 Agent 项目的能力。

---

# 建议给自己的练习

为了避免一路只复制代码，每完成一个阶段都做一个小变化：

- 第 4 章：自己增加 `GET /hello`；
- 第 5 章：自己增加一个 POST 请求字段；
- 第 10 章：自己查询某个 session 的 messages；
- 第 15 章：新增 `multiply` Tool；
- 第 16 章：让 Registry 自动找到它；
- 第 18 章：把 `max_steps` 改成 3，观察停止行为；
- 第 19 章：让 `run_python` 计算斐波那契数；
- 第 20 章：给网页增加“新会话”按钮。

---

# 发布教程时建议补的真实截图

仓库中的 SVG 是概念教学图。

为了让 GitHub 首页更有说服力，建议再补 3 张你自己的真实运行截图：

1. FastAPI `/docs`；
2. Agent 调用 `run_python` 的 Terminal 日志；
3. 最终浏览器网页。

详细清单见：

```text
docs/SCREENSHOTS.md
```

截屏时不要暴露 `.env`、API Key 或 Token。

---

# 官方资料

OpenAI：

- Responses API: https://developers.openai.com/api/docs/guides/responses
- Function Calling: https://developers.openai.com/api/docs/guides/function-calling
- Streaming Responses: https://developers.openai.com/api/docs/guides/streaming-responses

E2B：

- https://e2b.dev/
- https://github.com/e2b-dev/code-interpreter

---

# 从这个 Mini Agent 到真实大型项目

这个仓库故意保持简单。

真实 Agent 项目还可能增加：

```text
认证与权限
PostgreSQL / Redis
任务队列
多用户并发
文件与对象存储
重试机制
Token / 成本控制
Tracing / Observability
更复杂的 Workflow
多 Agent
前端状态管理
部署与 CI/CD
```

但不要因此认为你现在学的东西是“假的”。

大型项目通常仍然建立在这些基本关系上：

```text
HTTP 请求
↓
Service
↓
LLM
↓
Tool
↓
执行环境
↓
State / Persistence
↓
返回结果
```

先把骨架亲手写懂，再阅读大型 Agent 项目，你会发现它们主要是在这个骨架上增加工程能力。

---

# License

教程代码使用 MIT License。

如果你在自己的项目中复制其他开源仓库的代码，请另外检查对方的 License。