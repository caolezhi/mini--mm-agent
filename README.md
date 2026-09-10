# 从 0 到 1 手写一个 Mini AI Agent

> 面向初学者：从 **Python + FastAPI** 开始，一步步写到 **Responses API、上下文、SQLite、流式输出、Tool Calling、Agent Loop、E2B Sandbox 和最小网页前端**。

这不是一个“复制最终代码就结束”的 Demo。

这份仓库更像一本很小的实战教材：我们会从最简单的 `print()` 开始，每次只增加一个新概念，并反复回答下面几个问题：

- 为什么现在需要它？
- 它解决了什么问题？
- 核心代码是什么意思？
- 正常运行后应该看到什么？
- 出错时应该从哪一层排查？
- 如果不看答案，你能不能自己再写一次？

**本项目不涉及数学建模。** 它实现的是一个通用、简化、适合学习底层原理的 AI Agent。

> 本教程统一使用 **Responses API**。如果你使用第三方 OpenAI-compatible API，请先确认供应商确实支持 Responses API；“兼容 OpenAI API”并不一定代表实现了所有接口。

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

这份教程适合：

- 会一点 Python，但没有写过完整后端；
- 知道大模型 API，却不知道 Agent 项目怎么组织；
- 一看到 `async/await`、FastAPI、数据库、Tool Calling 就觉得东西太多；
- 能运行别人的项目，但不知道如果从空文件夹开始应该怎么写；
- 想先搞懂 Agent 底层逻辑，再去学习 LangGraph、LangChain 或更大的开源项目。

我们**故意不使用 Agent 框架**，因为这里的目标不是记住某个框架 API，而是先看见 Agent 最核心的骨架。

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

仓库中放的是**最终版本代码**。学习时建议按照下面的章节一步一步写，不要一开始就把所有最终代码复制过去。

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

# 第 1 章：Windows + WSL + VSCode —— 先把开发环境接通

> **本章目标**：让 Windows 上的 VSCode 真正连接到 WSL Ubuntu。  
> **完成效果**：VSCode 左下角显示 `WSL: Ubuntu...`，终端路径位于 `/home/...`。  
> **核心知识**：Windows 与 WSL 的关系、Linux 文件系统、VSCode 远程开发。

你的电脑虽然是 Windows，但我们希望真正的开发环境是：

```text
Windows
│
├── VSCode 图形界面
│     ↓ WSL 扩展
│
└── WSL Ubuntu
      ├── 项目文件
      ├── Python
      ├── pip
      ├── Git
      └── Terminal
```

VSCode 可以把界面运行在 Windows，同时让当前工作区和程序真正运行在 Ubuntu 中。

## 1.1 连接 WSL

Windows VSCode 安装 Microsoft 官方 **WSL** 扩展，然后：

```text
Ctrl + Shift + P
→ WSL: Connect to WSL
→ Ubuntu-24.04（或你的 Ubuntu 版本）
```

正常情况下 VSCode 左下角会显示：

```text
WSL: Ubuntu-24.04
```

打开：

```text
Terminal → New Terminal
```

运行：

```bash
pwd
python3 --version
git --version
```

`pwd` 应该类似：

```text
/home/yourname
```

如果看到 `C:\...`，说明你开的还是 Windows Terminal。

## 1.2 为什么项目建议放 `/home/...`？

WSL 虽然也能访问 `/mnt/c/...`，但初学阶段建议把项目放在：

```text
/home/你的用户名/
```

这样路径、权限、虚拟环境和以后 Linux 部署的思维更一致。

## 1.3 Python 扩展也要在 WSL 中启用

连接 WSL 后，在 Extensions 中搜索 Microsoft 官方 **Python**。

如果看到：

```text
Install in WSL: Ubuntu-24.04
```

就点击安装。

### 本章检查

```text
[ ] VSCode 左下角显示 WSL: Ubuntu
[ ] pwd 输出 /home/你的用户名
[ ] python3 --version 正常
[ ] git --version 正常
```

### 小练习

```bash
pwd
whoami
ls
```

尝试解释这三个命令分别在回答什么问题。

---

# 第 2 章：创建项目与 Python 虚拟环境 —— 给项目一个独立的小房间

> **本章目标**：创建项目目录和独立 Python 环境。  
> **完成效果**：终端出现 `(.venv)`，`which python` 指向项目里的 `.venv/bin/python`。  
> **核心知识**：venv、依赖隔离、Python Interpreter。

## 2.1 创建项目

```bash
cd ~
mkdir mini--mm-agent
cd mini--mm-agent
pwd
```

应该类似：

```text
/home/yourname/mini--mm-agent
```

## 2.2 为什么需要 `.venv`？

不同 Python 项目可能需要不同版本的第三方包。

虚拟环境相当于：

```text
mini--mm-agent/
└── .venv/
    ├── 自己的 python
    ├── 自己的 pip
    └── 自己安装的依赖
```

创建：

```bash
python3 -m venv .venv
```

激活：

```bash
source .venv/bin/activate
```

检查：

```bash
which python
python --version
which pip
```

正确的 `python` 路径应该位于：

```text
.../mini--mm-agent/.venv/bin/python
```

如果 Ubuntu 缺少 venv：

```bash
sudo apt update
sudo apt install python3-venv
```

## 2.3 让 VSCode 选择同一个解释器

```text
Ctrl + Shift + P
→ Python: Select Interpreter
→ ./.venv/bin/python
```

其他项目也可以叫 `.venv`，因为真正完整路径不同，所以不会冲突。

### 小练习

```bash
deactivate
source .venv/bin/activate
```

观察终端前 `(.venv)` 的变化。

---

# 第 3 章：运行第一个 Python 文件 —— 先证明最基础链路是通的

> **本章目标**：创建源码目录并运行第一个 Python 程序。  
> **完成效果**：终端输出 `Hello Mini Agent`。  
> **核心知识**：Python 文件、保存、逐层验证。

创建：

```bash
mkdir app
touch app/main.py
```

`app/main.py`：

```python
print("Hello Mini Agent")
```

记得：

```text
Ctrl + S
```

然后运行：

```bash
python app/main.py
```

应该得到：

```text
Hello Mini Agent
```

如果 VSCode 标签旁边还有小圆点，说明文件可能还没有保存。Python 执行的是磁盘中的文件，而不是尚未保存的编辑器内容。

这一章看起来非常简单，但它建立了一个重要开发习惯：

```text
先验证 Python
↓
再验证 FastAPI
↓
再验证 HTTP
↓
再验证模型
↓
再验证 Tool
↓
最后组合 Agent
```

---

# 第 4 章：第一次启动 FastAPI —— 把 Python 函数变成 Web API

> **本章目标**：让浏览器可以访问 Python 后端。  
> **完成效果**：浏览器访问 `127.0.0.1:8001` 能看到 JSON，并能打开 `/docs`。  
> **核心知识**：FastAPI、Uvicorn、Route、端口。

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

运行：

```bash
uvicorn app.main:app --reload --port 8001
```

浏览器打开：

```text
http://127.0.0.1:8001
http://127.0.0.1:8001/docs
```

`uvicorn app.main:app` 可以拆成：

```text
uvicorn
→ 启动 Web Server

app.main
→ 找 app/main.py

:app
→ 找 main.py 中的 app = FastAPI()
```

`@app.get("/")` 可以先读成人话：

> 当有人用 GET 请求访问 `/`，执行下面的 `home()`。

而 Python 字典返回值会被 FastAPI 转成 JSON 响应。

如果端口被占用：

```bash
ss -ltnp | grep :8001
```

或者临时使用 8002。

### 小练习

新增：

```python
@app.get("/hello")
def hello():
    return {"message": "Hello from /hello"}
```

然后观察 `/docs` 是否多出一个接口。

---

# 第 5 章：GET、POST、Header 和 JSON —— 数据到底怎么进入后端？

> **本章目标**：写出第一个接收 JSON 的 POST API。  
> **完成效果**：能用 Swagger 和 curl 向 `/responses` 发送 JSON。  
> **核心知识**：HTTP Method、URL、Header、Body、Pydantic、状态码。

浏览器地址栏默认发送 GET。

但如果用户要把一份数据交给服务器处理，例如：

```json
{
  "input": "你好"
}
```

我们使用 POST。

一个 HTTP 请求先认识四部分：

```text
Method  → POST
URL     → /responses
Headers → Content-Type: application/json
Body    → {"input":"你好"}
```

修改 `app/main.py`：

```python
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class ResponseRequest(BaseModel):
    input: str


@app.get("/")
def home():
    return {"message": "Hello Mini Agent"}


@app.post("/responses")
def create_response(request: ResponseRequest):
    return {
        "output": f"你输入了：{request.input}"
    }
```

`BaseModel` 在告诉 FastAPI：

> 请求 Body 必须有一个字符串类型的 `input` 字段。

打开 `/docs`，发送：

```json
{
  "input": "你好，我正在学习 Agent"
}
```

正常返回 200。

也可以用 curl：

```bash
curl -X POST http://127.0.0.1:8001/responses \
  -H "Content-Type: application/json" \
  -d '{"input":"你好，我是从终端发过来的"}'
```

这里：

```text
-X POST → Method
URL     → 请求地址
-H      → Header
-d      → Body
```

常见状态码：

```text
200 → 成功
404 → 路径/资源没找到
405 → Method 不允许
422 → 请求数据没通过验证
500 → 服务器内部代码出错
```

如果把 `-X` 写成小写 `-x`，curl 会把 `POST` 当作代理地址，可能报：

```text
Could not resolve proxy: POST
```

### 小练习

把请求模型临时改成：

```python
class ResponseRequest(BaseModel):
    input: str
    user_name: str
```

自己修改 Swagger JSON，让返回值中包含名字。练习完成后恢复为只有 `input`。

---

# 第 6 章：`.env` —— 把“配置”和“源码”分开

> **本章目标**：让程序从 `.env` 读取 API Key、Base URL 和模型名。  
> **完成效果**：Python 能读出配置，但真实密钥不会进入 GitHub。  
> **核心知识**：环境变量、dotenv、`.env.example`、`.gitignore`、秘密管理。

从这一章开始，我们马上要调用真正的大模型 API。

这意味着程序需要知道三件东西：

```text
API_KEY
→ 你是谁 / 你有没有调用权限

BASE_URL
→ 请求应该发到哪个 API 服务器

MODEL_NAME
→ 这次要使用哪个模型
```

以后执行 Python 沙箱时，还会增加：

```text
E2B_API_KEY
```

## 6.1 为什么不能直接写在 Python 代码里？

最简单的写法当然是：

```python
API_KEY = "sk-xxxxxxxxxxxxxxxx"
```

程序确实能运行。

但如果你之后：

```bash
git add .
git commit
git push
```

真实 Key 很可能跟着源码一起上传 GitHub。

这会产生两个问题：

1. 别人可能使用你的额度；
2. 即使后来删除那一行，Key 也可能已经进入 Git 历史。

所以我们把：

```text
程序逻辑
```

和：

```text
运行配置 / 密钥
```

分开。

---

## 6.2 安装 `python-dotenv`

确认虚拟环境仍然激活：

```text
(.venv)
```

执行：

```bash
pip install python-dotenv
```

这个库的作用很简单：

> 帮 Python 从 `.env` 文件中加载环境变量。

---

## 6.3 在项目根目录创建 `.env`

注意位置。

现在应该是：

```text
mini--mm-agent/
├── .venv/
├── .env           ← 创建在这里
└── app/
    └── main.py
```

创建：

```bash
touch .env
```

或者直接在 VSCode Explorer 中新建 `.env`。

先写测试值：

```env
API_KEY=test-key
BASE_URL=https://example.com/v1
MODEL_NAME=test-model
E2B_API_KEY=
```

这里暂时不用放真实 Key。

我们先验证“配置读取链路”本身是通的。

---

## 6.4 `.env` 为什么通常不用写引号？

下面这种写法完全可以：

```env
MODEL_NAME=test-model
BASE_URL=https://example.com/v1
```

`python-dotenv` 读取以后，Python 得到的仍然是字符串。

也可以写：

```env
MODEL_NAME="test-model"
```

如果值中包含空格或一些特殊字符，加英文引号会更清楚。

不要写成中文弯引号：

```text
“test-model”
```

环境变量还有一个很重要的特点：

```env
PORT=8001
```

读取出来通常仍然是字符串：

```python
"8001"
```

如果真的需要整数，需要自己转换：

```python
port = int(os.getenv("PORT"))
```

---

## 6.5 创建 `app/config.py`

创建：

```bash
touch app/config.py
```

写：

```python
import os

from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
E2B_API_KEY = os.getenv("E2B_API_KEY")
```

保存。

### `import os` 是什么？

`os` 是 Python 标准库的一部分。

我们这里主要用：

```python
os.getenv(...)
```

读取环境变量。

### `load_dotenv()` 是什么？

可以先理解成：

```text
.env 文件
↓
load_dotenv()
↓
把里面的键值对加载进当前 Python 进程的环境变量
```

然后：

```python
os.getenv("MODEL_NAME")
```

就可以取出：

```text
test-model
```

---

## 6.6 测试配置是否真的读到了

在项目根目录执行：

```bash
python -c "from app.config import MODEL_NAME; print(MODEL_NAME)"
```

应该输出：

```text
test-model
```

再测试：

```bash
python -c "from app.config import BASE_URL; print(BASE_URL)"
```

应该输出：

```text
https://example.com/v1
```

### 为什么不建议测试时直接打印真实 API Key？

因为以后你可能：

- 截图终端；
- 录屏；
- 把报错复制到 issue；
- 把日志贴给别人。

如果养成 `print(API_KEY)` 的习惯，Key 很容易意外泄漏。

验证配置时优先打印：

```text
MODEL_NAME
BASE_URL
```

即可。

---

## 6.7 一个非常经典的错误：文件没保存

如果代码明明写了：

```python
MODEL_NAME = os.getenv("MODEL_NAME")
```

但运行：

```bash
python -c "from app.config import MODEL_NAME; print(MODEL_NAME)"
```

却得到：

```text
ImportError: cannot import name 'MODEL_NAME' from 'app.config'
```

先不要怀疑 `dotenv`。

执行：

```bash
cat app/config.py
```

看看磁盘上的文件到底是什么。

如果终端看到的是旧内容，很可能 VSCode 还没保存。

按：

```text
Ctrl + S
```

然后再测试。

这也是为什么前面一直强调“磁盘上的文件”和“编辑器当前显示的内容”并不永远同步。

---

## 6.8 创建 `.gitignore`

项目根目录创建：

```text
.gitignore
```

写：

```gitignore
.venv/
.env
__pycache__/
*.pyc
chat.db
```

这里最关键的是：

```gitignore
.env
```

意思是：

> Git 默认不要追踪真实 `.env`。

可以检查：

```bash
git status
```

真实 `.env` 不应该出现在准备提交的文件列表中。

---

## 6.9 为什么仓库里还要有 `.env.example`？

如果 `.env` 不上传 GitHub，别人 clone 你的项目以后怎么知道应该配置哪些变量？

所以再创建：

```text
.env.example
```

内容：

```env
API_KEY=
BASE_URL=https://api.openai.com/v1
MODEL_NAME=your-responses-compatible-model
E2B_API_KEY=
```

`.env.example` 只告诉别人：

> “这个项目需要哪些配置。”

但里面不放真实秘密。

所以最终是：

```text
.env
→ 本机真实配置，不提交

.env.example
→ 配置模板，可以提交
```

---

## 6.10 现在换成你的真实模型配置

完成上面的 `test-model` 测试后，再把 `.env` 改成你自己的：

```env
API_KEY=你的真实Key
BASE_URL=你的真实BaseURL
MODEL_NAME=你的真实模型名
E2B_API_KEY=
```

不要把 Key 发到 issue、README、截图或聊天记录里。

如果你使用第三方 API，先确认它是否真的实现了 **Responses API**。

---

### 第 6 章检查清单

```text
[ ] python-dotenv 已安装
[ ] 根目录有 .env
[ ] app/config.py 能读取 MODEL_NAME
[ ] 根目录有 .gitignore
[ ] .env 被 .gitignore 忽略
[ ] 有可以公开提交的 .env.example
[ ] 没有把真实 API Key 打印或提交到 GitHub
```

### 本章小练习

在 `.env` 增加：

```env
PROJECT_NAME=Mini Agent
```

在 Python 中读取并打印它。

练习结束后可以删除这个测试字段。

### 你现在应该能回答

> `.env` 和 `.env.example` 为什么要同时存在？它们最大的区别是什么？

---

# 第 7 章：第一次调用 Responses API —— 让 Python 真正和大模型说上话

> **本章目标**：暂时不做 Agent，只验证 Python 可以调用大模型。  
> **完成效果**：终端打印模型真实返回的文字。  
> **核心知识**：SDK、Client、Responses API、`model`、`instructions`、`input`、`output_text`。

到这一章之前，我们已经有两条独立链路：

```text
Python → 能运行
```

以及：

```text
HTTP → FastAPI → 能接收 JSON
```

现在先建立第三条：

```text
Python
↓
大模型 API
↓
模型回答
```

注意：这一章仍然**不做 Tool Calling，也不做 Agent Loop**。

原因还是同一个：先把每一层单独验证通。

---

## 7.1 SDK 是什么？

理论上，你可以自己手写 HTTP 请求去调用模型服务器。

但官方 SDK 已经帮我们处理了很多重复工作，例如：

```text
Authorization Header
JSON 请求构造
Response 对象解析
网络连接
错误类型
```

所以我们安装 Python SDK：

```bash
pip install openai
```

确认：

```bash
pip show openai
```

---

## 7.2 创建 `app/llm.py`

项目现在变成：

```text
mini--mm-agent/
├── .env
├── .env.example
├── .gitignore
└── app/
    ├── main.py
    ├── config.py
    └── llm.py      ← 新建
```

创建：

```bash
touch app/llm.py
```

先写最简单的**同步版本**：

```python
from openai import OpenAI

from app.config import API_KEY, BASE_URL, MODEL_NAME


client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)


def ask_model(user_input: str):
    response = client.responses.create(
        model=MODEL_NAME,
        instructions="你是一个简洁、清楚的 AI 助手。",
        input=user_input,
    )

    return response.output_text
```

为什么现在先用同步 `OpenAI`，而不是马上上 `AsyncOpenAI`？

因为这一章只想回答一个问题：

> **“模型 API 到底能不能成功调用？”**

异步会在后面进入 Web 服务时再引入。

---

## 7.3 `client = OpenAI(...)` 是什么？

```python
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)
```

可以理解成：

> 创建一个“模型 API 客户端”。

其中：

```text
api_key
→ 用来认证

base_url
→ 告诉 SDK 请求发给哪个服务
```

如果你使用 OpenAI 官方 API，通常使用官方 Base URL。

如果你使用第三方兼容服务，则填它提供的地址。

---

## 7.4 `client.responses.create(...)` 到底在发送什么？

核心：

```python
response = client.responses.create(
    model=MODEL_NAME,
    instructions="你是一个简洁、清楚的 AI 助手。",
    input=user_input,
)
```

先认识三个字段。

### `model`

```python
model=MODEL_NAME
```

告诉服务：

> 这次请求使用哪个模型。

### `input`

```python
input=user_input
```

就是当前真正要交给模型处理的输入。

例如：

```text
请用一句话解释什么是 AI Agent
```

### `instructions`

```python
instructions="你是一个简洁、清楚的 AI 助手。"
```

它用于告诉模型更高层的行为要求。

可以先把它理解成：

```text
instructions
→ 你应该以什么方式工作

input
→ 这一次用户具体问什么
```

---

## 7.5 为什么是 `response.output_text`？

调用成功后返回的是一个 Response 对象。

Responses API 的 `output` 不一定只有纯文本；以后还可能出现：

```text
message
function_call
reasoning item
其他类型的 output item
```

如果我们这一章只想取得最终文字，SDK 提供了方便的：

```python
response.output_text
```

所以：

```python
return response.output_text
```

就能取得模型生成的文本。

等到 Tool Calling 章节，我们会开始直接查看：

```python
response.output
```

---

## 7.6 直接在终端测试，不要急着改 FastAPI

执行：

```bash
python -c "from app.llm import ask_model; print(ask_model('你好，请只回答：连接成功'))"
```

如果配置正常，你应该看到类似：

```text
连接成功
```

模型也可能加少量标点或不同措辞，只要确实返回正常文本即可。

这说明：

```text
.env
↓
config.py
↓
llm.py
↓
SDK
↓
Responses API
↓
模型
↓
Python 得到 output_text
```

整个链路已经通了。

---

## 7.7 如果报错，应该先看哪一层？

常见情况：

### 401 / Authentication 错误

优先检查：

```text
API_KEY
```

### 404 / Endpoint 不存在

优先检查：

```text
BASE_URL
第三方服务是否支持 Responses API
```

### model not found

检查：

```text
MODEL_NAME
```

### Connection / Timeout

可能是：

```text
网络
代理
第三方服务状态
BASE_URL
```

不要一看到错误就同时改十个地方。

先根据错误类型缩小范围。

---

## 7.8 为什么“OpenAI-compatible”仍然可能调用失败？

第三方服务写“OpenAI-compatible”时，可能表示：

```text
兼容某些请求格式
```

但不一定意味着：

```text
Responses API
Function Calling
Streaming Events
所有字段
```

全部兼容。

所以这个教程如果用第三方服务，至少要确认：

```text
是否有 /responses
是否支持你要使用的模型
后面是否支持 function tools
```

---

### 第 7 章检查清单

```text
[ ] openai Python SDK 已安装
[ ] app/llm.py 已创建
[ ] OpenAI client 能初始化
[ ] client.responses.create 能成功返回
[ ] 能解释 model / input / instructions
[ ] 能通过 response.output_text 得到文字
```

### 本章小练习

不要改任何其他代码，只把测试问题换成：

```text
请用三句话解释 FastAPI 是什么
```

确认模型能正常回答。

### 你现在应该能回答

> 到目前为止，这个程序是不是 Agent？为什么？

答案应该是：**还不是。**

现在它只是一个能调用大模型的 Python 程序，还没有工具和 Agent Loop。

---

# 第 8 章：把 Responses API 接进 FastAPI —— 从脚本变成真正的 AI 后端

> **本章目标**：让 `POST /responses` 不再复读用户，而是返回真实模型回答。  
> **完成效果**：Swagger 中提交一句话，后端调用模型后返回结果。  
> **核心知识**：HTTP → Python → 模型 API、同步与异步、LLM Gateway。

![一次请求是如何流动的](docs/images/request-flow.svg)

现在我们手上已经有：

```text
第 5 章：POST /responses 能收 JSON

第 7 章：ask_model() 能调用真实模型
```

这一章做的事情就是把两条链拼起来：

```text
POST /responses
↓
FastAPI
↓
模型 API
↓
返回回答
```

---

## 8.1 先看最直觉的写法

理论上可以直接在 `main.py` 中：

```python
@app.post("/responses")
def create_response(request: ResponseRequest):
    reply = ask_model(request.input)
    return {"output": reply}
```

这已经可以工作。

但我们的模型调用属于网络 I/O。

后端以后可能同时服务多个请求，所以现在开始引入异步版本。

---

## 8.2 把 `OpenAI` 改成 `AsyncOpenAI`

打开 `app/llm.py`，改成：

```python
from openai import AsyncOpenAI

from app.config import API_KEY, BASE_URL, MODEL_NAME


client = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)


DEFAULT_INSTRUCTIONS = (
    "你是一个简洁、清楚的 AI 助手。"
)


async def create_model_response(
    input_data,
    *,
    instructions: str = DEFAULT_INSTRUCTIONS,
    previous_response_id: str | None = None,
):
    kwargs = {
        "model": MODEL_NAME,
        "instructions": instructions,
        "input": input_data,
    }

    if previous_response_id:
        kwargs["previous_response_id"] = previous_response_id

    return await client.responses.create(**kwargs)
```

现在先不要管：

```python
previous_response_id
```

它是下一章的主角。

这一章只关注：

```python
async def
await
```

---

## 8.3 `async def` 和 `await` 先怎么理解？

网络请求经常需要等待：

```text
你的 Python
↓ 发请求
网络中等待
↓
模型服务器生成
↓
结果回来
```

等待网络期间，CPU 并不是一直在做有意义的计算。

所以异步代码允许事件循环在等待时处理别的工作。

先用一个不完全严谨、但很实用的理解：

```text
async def
→ 这个函数可以进行异步等待

await
→ 这里要等一个异步操作完成
```

并且通常：

```python
await ...
```

要写在：

```python
async def ...
```

里面。

---

## 8.4 为什么加一层 `create_model_response()`？

你可能会问：

> 为什么不在每个 API Route 中直接写 `client.responses.create()`？

因为以后：

```text
普通回答
流式回答
Agent
工具循环
```

都会调用同一个模型服务。

如果每个地方都自己初始化 SDK 和配置：

```text
BASE_URL 到处出现
MODEL_NAME 到处出现
公共 instructions 到处出现
```

维护会越来越乱。

所以我们把 `llm.py` 当作一个很小的 **LLM Gateway**：

```text
项目其他模块
↓
create_model_response(...)
↓
llm.py
↓
真正知道 SDK / API_KEY / BASE_URL / MODEL_NAME
```

---

## 8.5 修改 `app/main.py`

这一阶段先不做工程分层，直接把模型接进去：

```python
from fastapi import FastAPI
from pydantic import BaseModel

from app.llm import create_model_response


app = FastAPI()


class ResponseRequest(BaseModel):
    input: str


@app.get("/")
def home():
    return {"message": "Hello Mini Agent"}


@app.post("/responses")
async def create_response(request: ResponseRequest):
    response = await create_model_response(
        request.input
    )

    return {
        "output": response.output_text
    }
```

注意这里的传播关系：

```text
client.responses.create 是异步
       ↑
create_model_response() 变 async
       ↑
调用它的 API Route 也变 async
```

---

## 8.6 测试真正的 AI API

如果 Uvicorn 已经停止：

```bash
uvicorn app.main:app --reload --port 8001
```

打开：

```text
http://127.0.0.1:8001/docs
```

调用：

```text
POST /responses
```

Body：

```json
{
  "input": "请用一句话解释什么是 AI Agent"
}
```

现在返回的 `output` 应该是模型真实生成的内容，而不是：

```text
你输入了：...
```

链路已经变成：

```text
Swagger / curl
↓ POST JSON
FastAPI
↓
create_model_response()
↓
Responses API
↓
response.output_text
↓
FastAPI JSON Response
```

---

## 8.7 为什么这一章还不马上拆 `routes.py / services/`？

因为我们希望你先看清楚主线。

现在只有：

```text
main.py
↓
llm.py
```

非常容易理解。

等业务继续增加：

```text
Session
SQLite
Reset
Streaming
Agent
```

`main.py` 开始变大以后，第 12 章再进行重构。

这比一开始就给你七八个文件夹更容易理解“为什么要分层”。

---

### 第 8 章检查清单

```text
[ ] app/llm.py 已切换为 AsyncOpenAI
[ ] create_model_response 是 async def
[ ] SDK 调用前使用 await
[ ] /responses Route 也是 async def
[ ] Swagger 能拿到真实模型回答
```

### 本章小练习

把：

```python
DEFAULT_INSTRUCTIONS
```

临时改成：

```text
你是一名 Python 老师，回答尽量使用初学者能理解的语言。
```

重新提同一个问题，观察回答风格有没有变化。

然后再恢复原设置。

### 你现在应该能回答

> 浏览器调用我们的 `/responses`，和我们的后端调用大模型 Responses API，是不是同一件请求？

不是。

它们是**两段不同的网络通信**：

```text
客户端 → 你的 FastAPI
```

以及：

```text
你的 FastAPI → 模型 API
```

---

# 第 9 章：多轮对话与 `previous_response_id` —— 模型为什么能“记住上一轮”？

> **本章目标**：让第二次模型请求可以继续第一轮上下文。  
> **完成效果**：先告诉模型一个信息，第二次请求能基于上一轮继续回答。  
> **核心知识**：Response ID、conversation state、`previous_response_id`、模型记忆的本质。

到目前为止，每一次调用都是独立的：

```text
请求 1：我叫小明
→ 模型回答

请求 2：我叫什么？
→ 如果没有上下文，模型不知道
```

一个常见误解是：

> “模型服务器是不是自动记住我刚才说了什么？”

不能这样理解。

连续对话需要某种**状态连接机制**。

Responses API 提供的一种方式就是：

```python
previous_response_id
```

---

## 9.1 每次 Response 都有自己的 `id`

例如：

```python
response1 = await client.responses.create(
    model=MODEL_NAME,
    instructions="你是一个AI助手。",
    input="我叫小明，请记住我的名字。",
)
```

返回对象里有：

```python
response1.id
```

它大概长得类似：

```text
resp_xxxxxxxxxxxxx
```

你可以把它理解成：

> “模型服务端这一轮 Response 的编号。”

---

## 9.2 第二轮把第一轮 ID 传回去

```python
response2 = await client.responses.create(
    model=MODEL_NAME,
    instructions="你是一个AI助手。",
    input="我叫什么名字？",
    previous_response_id=response1.id,
)
```

结构变成：

```text
第 1 轮
input = 我叫小明
↓
Response 1
id = resp_abc

第 2 轮
input = 我叫什么？
previous_response_id = resp_abc
↓
模型继续上一条 Response 的上下文
```

所以：

```python
previous_response_id
```

并不是“上一条文字答案”。

它是：

> **上一轮 Response 对象的 ID。**

---

## 9.3 先用一个独立脚本验证，不急着放进 FastAPI

可以临时新建：

```text
test_conversation.py
```

写：

```python
import asyncio

from app.llm import create_model_response


async def main():
    first = await create_model_response(
        "我叫小明，请记住我的名字。"
    )

    print("第一轮：", first.output_text)
    print("response id:", first.id)

    second = await create_model_response(
        "我叫什么名字？",
        previous_response_id=first.id,
    )

    print("第二轮：", second.output_text)


asyncio.run(main())
```

运行：

```bash
python test_conversation.py
```

第二轮正常情况下应该知道“小明”。

---

## 9.4 为什么我们每一轮仍然传 `instructions`？

在本教程的封装中：

```python
create_model_response(...)
```

每一轮都会重新设置当前请求需要的 `instructions`。

这样做的好处是：

```text
应用行为规则明确写在当前调用里
```

而不是依赖“上一轮也许已经设置过”。

对初学者来说，这种写法更容易追踪。

---

## 9.5 现在出现了一个新的后端问题

单个测试脚本很好办：

```python
first.id
```

直接存在变量里。

但真实 FastAPI 有很多请求。

比如：

```text
浏览器 A
上一轮 response_id = resp_111

浏览器 B
上一轮 response_id = resp_999
```

当下一条 HTTP 请求到来时，服务器必须知道：

> “你属于 A 还是 B？”

于是我们需要一个自己的：

```text
session_id
```

例如：

```text
session-a → resp_111
session-b → resp_999
```

这就是下一章数据库要保存的东西。

---

## 9.6 为什么不用一个全局变量？

你当然可以暂时写：

```python
previous_response_id = None
```

然后所有请求共享它。

单人实验似乎能工作。

但只要两个人同时使用：

```text
用户 A 的上一轮
↓
全局变量
↑
用户 B 的上一轮
```

就会互相覆盖，发生“串会话”。

所以真实后端不能只保存：

```text
一个 previous_response_id
```

而要保存：

```text
session_id → previous_response_id
```

---

## 9.7 一个需要知道的现实问题：Response ID 不是你自己的永久数据库

如果直接使用 OpenAI 官方 Responses API，Response 对象默认会由服务端保存一段时间；官方文档当前说明默认 Response 对象有保存策略，并且 `previous_response_id` 用来串联上下文。

但是：

- 你的应用仍然需要保存“哪个用户对应哪个 Response ID”；
- 第三方兼容服务的存储策略可能完全不同；
- 如果你未来需要长期历史、搜索、审计或迁移，只保存 Response ID 并不够。

所以我们下一章仍然会建立自己的 SQLite。

---

### 第 9 章检查清单

```text
[ ] 知道 response.id 是什么
[ ] 知道 previous_response_id 传的不是文本
[ ] 能完成两轮连续模型调用
[ ] 知道全局 previous_response_id 会导致用户串会话
[ ] 知道应用还需要自己的 session_id
```

### 本章小练习

把测试脚本改成三轮：

```text
第 1 轮：我最喜欢蓝色
第 2 轮：我最喜欢什么颜色？
第 3 轮：请把这个颜色翻译成英文
```

每次都把上一轮：

```python
response.id
```

作为下一轮的 `previous_response_id`。

### 你现在应该能回答

> “多轮对话记忆”最基础的本质是什么？

一个合格回答是：

> **下一轮请求必须能够重新获得上一轮上下文；`previous_response_id` 是 Responses API 提供的一种上下文连接方式。**

---

# 第 10 章：SQLite 保存 Session 与消息 —— 让服务器重启后还能找到会话

> **本章目标**：给每个 `session_id` 保存对应的 `previous_response_id`，并保存本地消息历史。  
> **完成效果**：FastAPI 重启以后，SQLite 数据仍然存在。  
> **核心知识**：SQLite、表、持久化、SELECT / INSERT / DELETE、Session 映射。

上一章我们的核心问题是：

```text
session-a → resp_111
session-b → resp_999
```

这个映射保存在哪里？

如果只放 Python 变量：

```python
sessions = {}
```

服务器一重启：

```text
内存清空
↓
sessions = {}
↓
映射消失
```

所以需要**持久化**。

---

## 10.1 什么叫“持久化”？

可以简单理解：

```text
内存
→ 程序关闭后通常消失

数据库 / 文件
→ 程序关闭后数据仍然存在
```

我们第一版选择 SQLite。

原因是它非常适合教学：

```text
不需要安装独立数据库服务器
不需要开端口
不需要数据库账号
一个文件就是数据库
```

最终你会在项目根目录看到：

```text
chat.db
```

---

## 10.2 为什么需要两张表？

我们保存：

```text
sessions
→ 当前 session 最新的 previous_response_id

messages
→ 我们自己的本地用户/助手历史
```

它们的职责不一样。

### `sessions`

回答：

> 当前这个浏览器下一次应该接哪一轮模型上下文？

例如：

```text
session-a | resp_111
session-b | resp_999
```

### `messages`

回答：

> 用户和助手实际说过什么？

例如：

```text
1 | session-a | user      | 我叫小明
2 | session-a | assistant | 你好小明
3 | session-a | user      | 我叫什么？
```

本地消息以后还可以用于：

- 网页展示历史；
- Debug；
- 审计；
- 数据迁移；
- 不再依赖某个模型供应商时重新构建上下文。

---

## 10.3 创建 `app/db.py`

```bash
touch app/db.py
```

先写：

```python
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "chat.db"
```

### 这一行路径代码是什么意思？

`__file__` 指当前：

```text
app/db.py
```

然后：

```text
.resolve()
→ 得到完整绝对路径

.parent
→ app/

.parent.parent
→ 项目根目录
```

最后：

```python
/ "chat.db"
```

所以数据库位置稳定在：

```text
mini--mm-agent/chat.db
```

而不是依赖你从哪个 Terminal 目录启动 Python。

---

## 10.4 初始化数据库

继续写：

```python
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                previous_response_id TEXT
            )
        """)
```

`CREATE TABLE IF NOT EXISTS` 可以读成：

> 如果表还不存在，就创建；如果已经存在，不要因为重复启动程序而报错。

---

## 10.5 保存一条消息

```python
def save_message(session_id: str, role: str, content: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO messages (session_id, role, content)
            VALUES (?, ?, ?)
            """,
            (session_id, role, content),
        )
```

这里的 SQL：

```sql
INSERT INTO messages ...
```

意思：

> 往 messages 表新增一行。

### 为什么 SQL 里面用 `?`，不自己拼字符串？

因为参数化查询更安全，也可以避免很多引号/转义问题。

不要写成：

```python
f"INSERT ... '{content}'"
```

这种字符串拼接方式以后容易出安全和格式问题。

---

## 10.6 查询某个 Session 的最新 Response ID

```python
def get_previous_response_id(session_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            """
            SELECT previous_response_id
            FROM sessions
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()

    return row[0] if row else None
```

这句 SQL：

```sql
SELECT previous_response_id
FROM sessions
WHERE session_id = ?
```

翻译成人话：

> 在 `sessions` 表里，找到这个 session，然后把它对应的 `previous_response_id` 给我。

如果没找到：

```python
None
```

代表这是新会话。

注意 Python 中只有一个元素的 tuple 要写：

```python
(session_id,)
```

最后那个逗号很重要。

---

## 10.7 保存 / 更新最新 Response ID

```python
def set_previous_response_id(session_id: str, response_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO sessions (session_id, previous_response_id)
            VALUES (?, ?)
            ON CONFLICT(session_id)
            DO UPDATE SET previous_response_id = excluded.previous_response_id
            """,
            (session_id, response_id),
        )
```

这段稍微高级一点。

它想表达的是：

```text
如果这个 session 以前不存在
→ INSERT

如果这个 session 已经存在
→ UPDATE 它最新的 response id
```

所以每个 session 只保留一个“当前最新 Response 指针”。

---

## 10.8 更新请求模型：增加 `session_id`

`app/main.py` 中：

```python
class ResponseRequest(BaseModel):
    session_id: str
    input: str
```

以后请求变成：

```json
{
  "session_id": "user-a",
  "input": "你好"
}
```

现在 FastAPI 不只知道：

```text
用户说了什么
```

还知道：

```text
这句话属于哪一个会话
```

---

## 10.9 把数据库和 Responses API 连起来

在 `app/main.py` 中导入：

```python
from app.db import (
    get_previous_response_id,
    init_db,
    save_message,
    set_previous_response_id,
)
```

创建 FastAPI 后初始化：

```python
app = FastAPI()

init_db()
```

然后把 `/responses` 改成：

```python
@app.post("/responses")
async def create_response(request: ResponseRequest):
    previous_response_id = get_previous_response_id(
        request.session_id
    )

    response = await create_model_response(
        request.input,
        previous_response_id=previous_response_id,
    )

    save_message(
        request.session_id,
        "user",
        request.input,
    )

    save_message(
        request.session_id,
        "assistant",
        response.output_text,
    )

    set_previous_response_id(
        request.session_id,
        response.id,
    )

    return {
        "output": response.output_text
    }
```

整个流程现在第一次变得比较像一个真正应用：

```text
POST /responses
↓
session_id = user-a
↓
SQLite 查询 user-a 的 previous_response_id
↓
Responses API
↓
模型回答
↓
保存 user 消息
↓
保存 assistant 消息
↓
更新 user-a 最新 response.id
↓
返回结果
```

---

## 10.10 测试两个不同 Session

打开 `/docs`。

先发送：

```json
{
  "session_id": "user-a",
  "input": "我叫小明，请记住我的名字。"
}
```

然后：

```json
{
  "session_id": "user-a",
  "input": "我叫什么名字？"
}
```

同一个 session 应该能够继续上下文。

接着换：

```json
{
  "session_id": "user-b",
  "input": "我叫什么名字？"
}
```

`user-b` 不应该自动获得 `user-a` 的上下文。

这就是：

```text
会话隔离
```

---

## 10.11 真正验证“持久化”：重启服务器

现在最关键的测试不是多问一次，而是：

1. 用 `user-a` 建立会话；
2. `Ctrl + C` 关闭 Uvicorn；
3. 重新启动 Uvicorn；
4. 再使用同一个 `session_id` 请求。

SQLite 文件仍然存在，所以我们的 session 映射不会因为 Python 内存清空而消失。

> 如果第三方 Responses API 本身不支持长期通过 `previous_response_id` 恢复上下文，那么本地 SQLite 虽然保存了 ID，供应商端仍可能无法解析它。第三方服务需要按自己的文档确认。

---

## 10.12 直接打开 SQLite 看看里面到底有什么

Ubuntu 如果没有 sqlite3 CLI：

```bash
sudo apt update
sudo apt install sqlite3
```

一定先确认当前目录：

```bash
pwd
```

应该是：

```text
/home/yourname/mini--mm-agent
```

然后：

```bash
sqlite3 chat.db
```

进入：

```text
sqlite>
```

查看表：

```sql
.tables
```

应该看到：

```text
messages  sessions
```

查看 Session：

```sql
SELECT * FROM sessions;
```

查看消息：

```sql
SELECT * FROM messages;
```

退出：

```sql
.quit
```

### 为什么有时会出现 `no such table: messages`？

一个非常经典的原因是：

你在：

```text
/home/yourname
```

执行：

```bash
sqlite3 chat.db
```

SQLite 发现这个文件不存在，就在当前目录创建了一个**新的空数据库**。

但真正数据库其实在：

```text
/home/yourname/mini--mm-agent/chat.db
```

所以遇到数据库奇怪问题时，第一反应先：

```bash
pwd
```

路径意识非常重要。

---

## 10.13 `SELECT / INSERT / DELETE` 先认识这三个词

这一阶段不用系统学习 SQL。

先记：

```text
SELECT
→ 查数据

INSERT
→ 新增数据

DELETE
→ 删除数据
```

后面 Reset 会使用 `DELETE`。

---

### 第 10 章检查清单

```text
[ ] 项目根目录出现 chat.db
[ ] messages 表存在
[ ] sessions 表存在
[ ] 同一个 session 可以继续上下文
[ ] 不同 session 不会串上下文
[ ] 能通过 sqlite3 CLI 查看数据
[ ] 知道 Python 内存和数据库持久化的区别
```

### 本章小练习

在 SQLite 中执行：

```sql
SELECT role, content
FROM messages
WHERE session_id = 'user-a';
```

尝试解释：

```text
SELECT
FROM
WHERE
```

各自在表达什么。

### 你现在应该能回答

> 为什么已经有 `previous_response_id`，我们还要自己使用 SQLite？

一个比较完整的回答应该包括：

1. 应用必须保存 `session_id → previous_response_id` 的映射；
2. 本地消息历史还有展示、调试、审计和迁移价值；
3. 我们不能把自己的应用状态完全寄托在 Python 内存里。

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

所以“会话重置”并不神秘，本质上就是清掉服务器保存的状态。

最终项目中的：

```python
def clear_session(session_id: str):
    ...
```

会同时删除这两部分数据。

---

# 第 12 章：把代码拆开 —— 从“能跑”到“能维护”

> **本章目标**：理解为什么真实项目会有很多文件夹。  
> **完成效果**：能说出 `routes.py / services / llm.py / db.py / tools.py` 各自负责什么。  
> **核心知识**：职责分离、项目分层、Service、Gateway。

![Mini Agent 项目结构](docs/images/project-structure.svg)

到这里，如果所有代码仍然写在 `main.py`，它会越来越长。

所以最终项目拆成：

```text
app/main.py
→ 组装 FastAPI

app/api/routes.py
→ HTTP 接口

app/services/response_service.py
→ 普通 Responses 业务

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

看到大型项目的 `api / services / infra / domain` 时，先问：

> **这一层的职责是什么？**

而不是试图一口气读完所有文件。

---

# 第 13 章：`async / await`、异常处理和日志

> **本章目标**：让项目开始具备真正后端的工程能力。  
> **完成效果**：模型 API 使用异步调用，错误有日志可查。  
> **核心知识**：异步 I/O、Exception、Logging。

前面已经第一次使用：

```python
async def
await
```

这一章把它系统化，并给 API 加错误处理：

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

日志比到处 `print()` 更适合真实服务：

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Agent 后面尤其会记录：

```python
logger.info("Agent step=%s", step + 1)
logger.info("执行工具 name=%s arguments=%s", name, arguments)
```

不要记录 API Key。

---

# 第 14 章：流式输出 —— 为什么回答可以一点点出现

> **本章目标**：实现 Responses API Streaming + SSE。  
> **完成效果**：终端/前端能一块一块收到模型文本。  
> **核心知识**：stream、event、`response.output_text.delta`、SSE、`yield`。

普通请求：

```text
模型全部生成
↓
一次性返回
```

流式请求：

```text
生成一点
↓
返回一点
↓
继续生成
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

FastAPI 再用：

```python
StreamingResponse(..., media_type="text/event-stream")
```

把增量继续转发给浏览器。

---

# 第 15 章：Tool Calling —— Chatbot 与 Agent 的分界线

> **本章目标**：让模型可以提出“调用函数”的请求。  
> **完成效果**：模型能够产生 `function_call`。  
> **核心知识**：Function Tool、JSON Schema、模型决策与程序执行的区别。

![Agent 为什么会调用工具](docs/images/tool-calling-loop.svg)

先写普通 Python 函数：

```python
def add_numbers(a: float, b: float):
    return a + b
```

再给模型一份 Tool Definition：

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

最重要的理解：

> **LLM 不会自己进入你的 Python 进程执行函数。模型只是产生 function call，请求你的程序执行。**

---

# 第 16 章：Tool Registry —— 怎么管理很多工具

> **本章目标**：避免不断写 `if / elif`。  
> **核心知识**：Registry、`json.loads()`、`**kwargs`。

```python
TOOL_REGISTRY = {
    "get_server_time": get_server_time,
    "add_numbers": add_numbers,
    "run_python": run_python,
}
```

模型返回工具名以后：

```python
tool_function = TOOL_REGISTRY.get(tool_name)
```

模型给的 JSON 参数字符串：

```python
tool_arguments = json.loads(tool_call.arguments)
```

再：

```python
tool_function(**tool_arguments)
```

自动把字典拆成函数关键字参数。

---

# 第 17 章：把真实工具结果交回模型

> **本章目标**：完成“模型请求工具 → 程序执行 → 结果回模型”。  
> **核心知识**：`function_call_output`、`call_id`。

模型 output 中找到：

```python
item.type == "function_call"
```

执行以后构造：

```python
{
    "type": "function_call_output",
    "call_id": tool_call.call_id,
    "output": str(tool_result),
}
```

`call_id` 用来告诉模型：

> 这个工具结果对应刚才的哪一次 function call。

---

# 第 18 章：Agent Loop —— 整个 Agent 的心脏

> **本章目标**：让模型可以连续完成多步任务。  
> **核心知识**：循环、工具结果、停止条件。

核心结构：

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
模型判断
↓
需要工具？
├─ 否 → 最终答案
└─ 是 → 执行工具
          ↓
        把结果交回模型
          ↓
        再次判断
```

一定设置 `max_steps`，避免 Agent 无限循环。

---

# 第 19 章：E2B Sandbox —— 不要在自己机器上 `exec()` 模型代码

> **本章目标**：安全执行模型生成的 Python。  
> **核心知识**：Sandbox、安全边界、通用代码执行工具。

安装：

```bash
pip install e2b-code-interpreter
```

`.env`：

```env
E2B_API_KEY=你的Key
```

最终 `app/sandbox.py`：

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

不要把模型代码直接：

```python
exec(model_generated_code)
```

运行在自己的真实服务器环境中。

---

# 第 20 章：加一个最小网页，把整个 Agent 串起来

> **本章目标**：网页输入任务，Agent 调工具以后把最终答案显示回来。  
> **核心知识**：HTML、JavaScript、fetch、CORS、session_id。

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

它和第 5 章的 curl 本质是同一种 HTTP 请求。

前端使用 `crypto.randomUUID()` 生成 session id，并存到 `localStorage`，让刷新页面后仍可复用同一个 session。

因为前端使用 3000、后端使用 8001，还要在 FastAPI 配置 CORS。

---

# 最终运行

## 1. 克隆项目

```bash
git clone https://github.com/caolezhi/mini--mm-agent.git
cd mini--mm-agent
```

## 2. 创建环境

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. 配置

```bash
cp .env.example .env
```

编辑：

```env
API_KEY=...
BASE_URL=...
MODEL_NAME=...
E2B_API_KEY=...
```

## 4. 启动后端

```bash
uvicorn app.main:app --reload --port 8001
```

Swagger：

```text
http://127.0.0.1:8001/docs
```

最终应该有：

```text
GET  /
POST /responses
POST /responses/stream
POST /responses/reset
POST /agent
```

## 5. 启动前端

新开 Terminal：

```bash
python3 -m http.server 3000 --directory frontend
```

打开：

```text
http://127.0.0.1:3000
```

测试：

```text
请使用 Python 工具计算 1 到 10000 所有整数的平方和
```

---

# 这个项目中最重要的 8 个概念

```text
FastAPI
→ 把 HTTP 请求映射成 Python

Responses API
→ 模型处理输入、生成文字或 function call

Session State
→ 区分不同会话

SQLite
→ 持久化本地状态

Tool Definition
→ 给模型看的工具说明书

Tool Registry / Executor
→ 真正找到并执行 Python 函数

Agent Loop
→ 模型 → 工具 → 结果 → 模型 的循环

Sandbox
→ 给模型生成代码加安全边界
```

---

# 如何判断自己是真的学会，而不是“跑起来”了？

## Level 1：能解释

不看源码回答：

1. GET 和 POST 有什么区别？
2. `.env` 和 `.env.example` 为什么都存在？
3. `response.output_text` 和 `response.id` 分别是什么？
4. `previous_response_id` 为什么能连接上下文？
5. 为什么应用还需要自己的 `session_id`？
6. Tool Definition 和 Python 函数有什么区别？
7. LLM 有没有真正执行工具？
8. Agent Loop 为什么要有 `max_steps`？
9. 为什么模型代码不应该直接 `exec()`？

## Level 2：闭卷重写

关掉教程，从空目录重新写：

```text
FastAPI
Responses API
Session
SQLite
一个 Tool
Tool Registry
Agent Loop
```

## Level 3：改需求

尝试自己增加：

```text
multiply(a, b)
read_text_file(path)
created_at 字段
Agent 超时
最大 Tool 调用次数
```

## Level 4：设计另一个项目

例如：

```text
文件分析 Agent
代码审查 Agent
科研文献 Agent
数据分析 Agent
```

这时候重点已经不是复制本项目，而是你能自己决定：

```text
Router 怎么设计？
Service 怎么拆？
状态放哪里？
有哪些 Tools？
哪些能力需要 Sandbox？
Agent 什么时候停止？
```

---

# 常见排错速查

```text
Address already in use
→ 检查端口

Method Not Allowed
→ 检查 GET / POST

422
→ 检查 Pydantic 请求字段

模型 401
→ 检查 API Key

模型 404
→ 检查 Base URL / Responses API 支持

模型 not found
→ 检查 MODEL_NAME

SQLite no such table
→ 先 pwd，确认打开的是正确 chat.db

logger.info 不显示
→ 检查 logging 配置是否被执行

Tool arguments = {}
→ 检查 JSON Schema 的 properties / required

E2B execution.text = None
→ 如果代码使用 print()，优先查看 execution.logs.stdout
```

---

# 官方资料

OpenAI：

- Responses / migration: https://developers.openai.com/api/docs/guides/migrate-to-responses
- Conversation state: https://developers.openai.com/api/docs/guides/conversation-state
- Function calling: https://developers.openai.com/api/docs/guides/function-calling
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
复杂 Workflow
多 Agent
部署与 CI/CD
```

但是它们通常仍然建立在这条主线上：

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

先把骨架亲手写懂，再阅读大型 Agent 项目，你会发现大型项目主要是在这个骨架上增加工程能力。

---

# License

教程代码使用 MIT License。

如果你在自己的项目中复制其他开源项目代码，请另外检查对方的 License。
