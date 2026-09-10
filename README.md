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

# 第 1 章：Windows + WSL + VSCode —— 先把开发环境接通

> **本章目标**：让 Windows 上的 VSCode 真正连接到 WSL Ubuntu。  
> **完成效果**：VSCode 左下角显示 `WSL: Ubuntu...`，新开的终端路径是 `/home/...`。  
> **核心知识**：Windows 与 WSL 的关系、Linux 文件系统、VSCode 远程开发。

这一章暂时不会写 Agent，也不会安装 FastAPI。

我们只解决一个最基础的问题：

> **以后我们到底在哪台“环境”里写代码和运行 Python？**

如果这个问题一开始没有搞清楚，后面很容易出现：

```text
Python 明明安装了，VSCode 却找不到
pip 明明装了包，运行时却说不存在
项目文件一会儿在 C:\，一会儿在 /home
终端命令在 Windows 能用，在 Ubuntu 又不能用
```

所以第一章先把地基打稳。

## 1.1 先理解我们要搭的环境

你的电脑是 Windows，但我们希望开发环境长这样：

```text
Windows
│
├── VSCode 图形界面
│     ↓ 通过 WSL 扩展连接
│
└── WSL Ubuntu
      ├── 项目文件
      ├── Python
      ├── pip
      ├── Git
      └── Terminal
```

这里最容易产生的误解是：

> “VSCode 装在 Windows，那 Python 是不是也一定跑在 Windows？”

不是。

VSCode 可以把界面运行在 Windows，同时把**当前工作区、终端、Python 扩展和程序执行环境**放在 WSL Ubuntu 中。

你可以把 VSCode 想成一个“遥控器”：

```text
VSCode 窗口在 Windows
        ↓
实际操作的是 Ubuntu 中的项目
```

这对后面的 Agent 项目很方便，因为真实服务器绝大多数也是 Linux 环境。

---

## 1.2 安装 VSCode 的 WSL 扩展

打开 Windows 上的 VSCode。

左侧点击 **Extensions（扩展）**，或者按：

```text
Ctrl + Shift + X
```

搜索：

```text
WSL
```

安装 Microsoft 官方的 **WSL** 扩展。

> 不要看到名字里有 WSL 的第三方扩展就随便装。初学阶段尽量使用 Microsoft 官方扩展。

安装完成后按：

```text
Ctrl + Shift + P
```

这会打开 VSCode 的 **Command Palette（命令面板）**。

搜索：

```text
WSL: Connect to WSL
```

选择你的 Ubuntu，例如：

```text
Ubuntu-24.04
```

VSCode 会重新打开一个窗口。

### 正常情况下你应该看到什么？

VSCode 左下角会出现类似：

```text
WSL: Ubuntu-24.04
```

看到这一行非常重要，它说明：

> **当前 VSCode 窗口已经进入 WSL 模式。**

---

## 1.3 打开 WSL Terminal

在这个已经连接 WSL 的 VSCode 窗口里，点击：

```text
Terminal → New Terminal
```

或者使用快捷键打开终端。

你可能看到类似：

```text
lezhi@DESKTOP-XXXXXXX:~$
```

这里：

```text
lezhi
→ Ubuntu 用户名

DESKTOP-XXXXXXX
→ 电脑名称

~
→ 当前位于自己的 Home 目录
```

输入：

```bash
pwd
```

`pwd` 是 **print working directory**，意思是：

> 告诉我“我现在在哪个目录”。

正常应该看到类似：

```text
/home/lezhi
```

你的用户名不同没关系，例如：

```text
/home/alice
/home/tom
```

都正常。

### 如果看到的是 `C:\...` 呢？

例如：

```text
C:\Users\xxx
```

那说明你当前开的还是 Windows Terminal，而不是 WSL Ubuntu Terminal。

先不要继续后面的步骤，回去确认 VSCode 左下角是否真的显示：

```text
WSL: Ubuntu...
```

---

## 1.4 检查 Ubuntu 中有没有 Python

继续在 WSL Terminal 输入：

```bash
python3 --version
```

例如：

```text
Python 3.12.3
```

版本数字不需要和这里一模一样。

本教程建议：

```text
Python 3.10+
```

如果命令能正常显示版本，就可以继续。

再检查 Git：

```bash
git --version
```

应该看到类似：

```text
git version 2.x.x
```

---

## 1.5 为什么项目建议放在 `/home/...`，而不是 `/mnt/c/...`？

WSL 可以访问 Windows 磁盘，例如：

```text
/mnt/c/Users/...
```

但本教程建议把项目直接建在：

```text
/home/你的用户名/
```

例如：

```text
/home/lezhi/mini--mm-agent
```

原因很简单：

- 文件权限更像正常 Linux；
- Python 虚拟环境更稳定；
- 大量小文件读写通常更自然；
- 路径更简单；
- 将来部署 Linux 服务器时思维一致。

这不是说 `/mnt/c` 绝对不能用，而是**初学阶段尽量减少额外变量**。

---

## 1.6 安装 Python 扩展时，为什么还要注意“安装到 WSL”？

很多人第一次会遇到：

```text
明明 Windows VSCode 已经安装 Python 扩展
为什么 WSL 里面还是没有 Python: Select Interpreter？
```

原因是：

```text
Windows VSCode 环境
和
WSL VSCode 环境
```

可以拥有不同的扩展状态。

在连接 WSL 后打开 Extensions，搜索 Microsoft 官方：

```text
Python
```

如果按钮显示：

```text
Install in WSL: Ubuntu-24.04
```

就点击安装。

后面我们选择虚拟环境时会用到它。

---

## 1.7 本章完成后的检查清单

现在先不要急着进入下一章。

确认下面四件事都成立：

```text
[ ] VSCode 左下角显示 WSL: Ubuntu
[ ] pwd 输出 /home/你的用户名
[ ] python3 --version 能看到 Python 版本
[ ] git --version 能正常输出
```

如果这四个都正常，你的开发环境第一层就接通了。

### 本章小练习

分别运行：

```bash
pwd
whoami
ls
```

尝试自己解释：

```text
pwd
→ 我现在在哪里？

whoami
→ 当前 Ubuntu 用户是谁？

ls
→ 当前目录里有什么？
```

### 你现在应该能回答

> VSCode 明明安装在 Windows 上，为什么我们仍然可以说“Python 在 Ubuntu 中运行”？

如果你能用自己的话解释清楚，再进入第 2 章。

---

# 第 2 章：创建项目与 Python 虚拟环境 —— 给项目一个独立的小房间

> **本章目标**：在 Ubuntu 的 Home 目录创建项目，并为它创建独立 Python 虚拟环境。  
> **完成效果**：终端前出现 `(.venv)`，`which python` 指向当前项目里的 `.venv/bin/python`。  
> **核心知识**：项目目录、`venv`、依赖隔离、Python Interpreter。

这一章要解决的问题是：

> **为什么不直接用系统 Python，而要专门创建 `.venv`？**

---

## 2.1 创建项目目录

确认你现在仍然在 WSL Terminal。

先回到自己的 Home：

```bash
cd ~
```

然后创建项目：

```bash
mkdir mini--mm-agent
```

进入项目：

```bash
cd mini--mm-agent
```

确认位置：

```bash
pwd
```

应该类似：

```text
/home/yourname/mini--mm-agent
```

例如：

```text
/home/lezhi/mini--mm-agent
```

此时这个目录还是空的。

运行：

```bash
ls -a
```

你大概率只会看到：

```text
.  ..
```

这里：

```text
.
→ 当前目录

..
→ 上一级目录
```

---

## 2.2 为什么需要虚拟环境？

假设你的电脑以后有两个 Python 项目：

```text
项目 A
需要某个库 1.x

项目 B
需要同一个库 2.x
```

如果所有库都安装进系统 Python：

```text
Ubuntu 的同一个 Python
├── 项目 A 的包
├── 项目 B 的包
├── 其他实验安装的包
└── 越来越乱
```

很容易出现版本冲突。

而虚拟环境相当于：

```text
mini--mm-agent/
└── .venv/
    ├── 自己的 python
    ├── 自己的 pip
    └── 自己安装的第三方库
```

所以不同项目可以各用各的。

---

## 2.3 创建 `.venv`

在项目根目录执行：

```bash
python3 -m venv .venv
```

这条命令可以拆开理解：

```text
python3
→ 使用 Python 3

-m venv
→ 运行 Python 自带的 venv 模块

.venv
→ 把虚拟环境创建在当前目录的 .venv 文件夹
```

如果成功，通常**不会输出“创建成功”**。

这很正常。

检查：

```bash
ls -a
```

现在应该多出：

```text
.venv
```

### 如果出现 `No module named venv` 或相关错误

Ubuntu 可能缺少 venv 包。

执行：

```bash
sudo apt update
sudo apt install python3-venv
```

然后重新运行：

```bash
python3 -m venv .venv
```

---

## 2.4 激活虚拟环境

执行：

```bash
source .venv/bin/activate
```

成功后终端前面通常会出现：

```text
(.venv)
```

例如：

```text
(.venv) lezhi@DESKTOP-XXXX:~/mini--mm-agent$
```

### `source` 是什么意思？

这里不用死记 Linux 原理。

你可以先理解成：

> 让当前 Terminal 开始使用 `.venv` 里面提供的 Python 环境。

---

## 2.5 确认现在到底用了哪个 Python

执行：

```bash
which python
```

正确结果应该类似：

```text
/home/yourname/mini--mm-agent/.venv/bin/python
```

再执行：

```bash
python --version
```

注意：

激活 `.venv` 以后，我们后面通常就可以写：

```bash
python
pip
```

而不必每次都写：

```bash
python3
```

再看看 pip：

```bash
which pip
pip --version
```

它也应该指向 `.venv`。

---

## 2.6 其他项目也有 `.venv`，名字一样会不会冲突？

不会。

因为名字一样，路径不同：

```text
/home/you/project-a/.venv
/home/you/project-b/.venv
/home/you/mini--mm-agent/.venv
```

真正决定你使用哪一个环境的是**完整路径**。

所以 `.venv` 是非常常见的项目虚拟环境目录名。

---

## 2.7 让 VSCode 也使用这个 `.venv`

Terminal 激活成功，不代表 VSCode 编辑器一定已经选择了同一个 Python。

按：

```text
Ctrl + Shift + P
```

搜索：

```text
Python: Select Interpreter
```

选择类似：

```text
.venv (Python 3.x)   ./.venv/bin/python
```

如果你看到了：

```text
Workspace
```

说明 VSCode 已经把这个解释器与当前项目关联。

### 点击解释器后“没反应”正常吗？

正常。

VSCode 往往不会弹一个“选择成功”的大窗口。

只要选择列表顶部显示：

```text
Selected Interpreter: ./.venv/bin/python
```

或者 VSCode 状态栏显示当前 Python 版本，就已经成功。

### 如果搜不到 `Python: Select Interpreter`

按顺序检查：

1. 当前 VSCode 左下角是不是 `WSL: Ubuntu`；
2. Microsoft Python 扩展是否安装在 WSL；
3. Python 扩展是否显示 `Enable (Workspace)`，如果是就点击启用；
4. 当前 Workspace 是否处于 Trusted 状态；
5. 执行 `Developer: Reload Window` 后再搜索。

---

## 2.8 本章完成后的目录

现在项目应该大概是：

```text
mini--mm-agent/
└── .venv/
```

暂时不要往 `.venv` 里手动创建自己的代码。

`.venv` 是工具生成的环境目录，我们自己的源码会单独放在 `app/`。

### 本章检查清单

```text
[ ] pwd 位于 /home/.../mini--mm-agent
[ ] ls -a 能看到 .venv
[ ] 终端前显示 (.venv)
[ ] which python 指向项目里的 .venv/bin/python
[ ] VSCode Select Interpreter 也选择了这个 .venv
```

### 本章小练习

执行：

```bash
deactivate
```

观察终端前面的 `(.venv)` 消失。

然后再：

```bash
source .venv/bin/activate
```

重新激活。

这样你会真正理解：

> `.venv` 并不是“开机以后永远自动生效”，而是当前 Terminal 可以进入或退出这个环境。

### 你现在应该能回答

> 为什么两个项目都可以有一个叫 `.venv` 的目录，却不会互相影响？

---

# 第 3 章：运行第一个 Python 文件 —— 先证明最基础的链路是通的

> **本章目标**：创建自己的源码目录，并运行第一个 Python 程序。  
> **完成效果**：终端输出 `Hello Mini Agent`。  
> **核心知识**：源码目录、Python 文件、保存文件、逐层验证。

终于开始写代码了。

不过这一章仍然不会写大模型。

原因是我们希望先验证：

```text
VSCode 编辑文件
↓
文件保存在 WSL
↓
.venv 中的 Python 读取文件
↓
程序真的运行
```

---

## 3.1 创建 `app` 目录

确认虚拟环境已经激活：

```text
(.venv)
```

在项目根目录执行：

```bash
mkdir app
```

然后创建文件：

```bash
touch app/main.py
```

当然，你也可以直接在 VSCode 左侧 Explorer 中：

```text
右键项目
→ New Folder
→ app

右键 app
→ New File
→ main.py
```

现在目录：

```text
mini--mm-agent/
├── .venv/
└── app/
    └── main.py
```

---

## 3.2 写第一行 Python

打开：

```text
app/main.py
```

写：

```python
print("Hello Mini Agent")
```

然后按：

```text
Ctrl + S
```

保存。

### 为什么我要特意提醒保存？

VSCode 文件标签右边如果有一个小圆点：

```text
main.py ●
```

通常代表文件还没有保存到磁盘。

Python 执行的是**磁盘上的文件**，不是你眼睛里尚未保存的编辑器内容。

这个小细节会在后面造成一个非常经典的困惑：

```text
我明明已经改代码了
为什么程序还在执行旧代码？
```

先养成：

```text
改完 → Ctrl + S → 再测试
```

的习惯。

---

## 3.3 从 Terminal 运行它

确保你当前目录是项目根目录：

```bash
pwd
```

类似：

```text
/home/yourname/mini--mm-agent
```

执行：

```bash
python app/main.py
```

应该看到：

```text
Hello Mini Agent
```

如果你看到这句话，这一章就成功了。

---

## 3.4 这条命令到底做了什么？

```bash
python app/main.py
```

可以拆成：

```text
python
→ 使用当前虚拟环境中的 Python 解释器

app/main.py
→ 把这个 Python 文件交给解释器执行
```

执行流程：

```text
Terminal
↓
.venv/bin/python
↓
读取 app/main.py
↓
执行 print(...)
↓
终端出现 Hello Mini Agent
```

这条链路看起来简单，却非常重要。

以后你的项目可能同时出现：

```text
FastAPI
Responses API
SQLite
Agent Loop
E2B
前端
```

如果一开始连“到底哪个 Python 在运行哪个文件”都不清楚，排错会非常痛苦。

---

## 3.5 为什么不直接一口气写 Agent？

因为真实开发很少是：

```text
写完 500 行
↓
一次运行
↓
祈祷成功
```

更好的方式是：

```text
先验证 Python
↓
再验证 FastAPI
↓
再验证 HTTP
↓
再验证大模型
↓
再验证 Tool Calling
↓
最后组合成 Agent
```

每次只增加一层。

这样报错时，你能大概知道：

> “刚才还是好的，只加了这一层以后坏了，那问题大概率就在这一层附近。”

这叫**逐层验证**。

---

## 3.6 本章小练习

不要复制下面答案，自己修改 `main.py`，让它输出两行：

```text
Hello Mini Agent
I am learning AI Agent
```

提示：可以写两个 `print()`。

完成后再把第二行删除，恢复：

```python
print("Hello Mini Agent")
```

因为下一章我们会把这个普通 Python 程序改造成 FastAPI Web 服务。

### 本章检查清单

```text
[ ] app/main.py 已创建
[ ] 文件已经 Ctrl + S 保存
[ ] python app/main.py 能运行
[ ] 输出 Hello Mini Agent
```

### 你现在应该能回答

> `python app/main.py` 中的 `python` 和 `app/main.py` 分别代表什么？

---

# 第 4 章：第一次启动 FastAPI —— 把 Python 函数变成可以访问的 Web API

> **本章目标**：把一个只能在 Terminal 运行的 Python 程序，变成浏览器可以访问的 Web 服务。  
> **完成效果**：浏览器访问 `http://127.0.0.1:8001` 能看到 JSON，并能打开 `/docs`。  
> **核心知识**：Web Server、FastAPI、Uvicorn、Route、Decorator、端口。

前面我们的程序只有这样：

```text
你在 Terminal 运行 Python
↓
Python 输出结果
```

但真正的 Agent 最后需要被：

```text
浏览器
其他程序
手机 App
前端网页
```

调用。

所以我们需要一个 Web API。

这就是 FastAPI 开始登场的地方。

---

## 4.1 先安装 FastAPI 和 Uvicorn

确保你仍然看得到：

```text
(.venv)
```

执行：

```bash
pip install fastapi uvicorn
```

这里装了两个东西。

### FastAPI

负责：

```text
定义“有哪些 HTTP 接口”
接收请求
把请求转换成 Python 参数
把 Python 返回值转换成 HTTP 响应
```

### Uvicorn

负责真正把 FastAPI 应用**运行成一个 Web Server**。

可以先粗略理解成：

```text
FastAPI
→ 你写网站后端规则

Uvicorn
→ 把这些规则真正跑起来，对外监听请求
```

安装后可以检查：

```bash
pip show fastapi
pip show uvicorn
```

---

## 4.2 把 `app/main.py` 改成 FastAPI

把原来的：

```python
print("Hello Mini Agent")
```

删除，改成：

```python
from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Hello Mini Agent"
    }
```

保存：

```text
Ctrl + S
```

现在不要急着背代码，我们逐块看。

---

## 4.3 `from fastapi import FastAPI` 是什么？

```python
from fastapi import FastAPI
```

意思是：

> 从安装好的 `fastapi` 包中，把 `FastAPI` 这个类拿进当前文件使用。

前一章我们只有 Python 自带的 `print()`。

现在开始使用第三方库提供的能力。

---

## 4.4 `app = FastAPI()` 是什么？

```python
app = FastAPI()
```

可以先理解成：

> 创建一个 FastAPI 后端应用对象，并把它放进变量 `app`。

以后：

```text
有哪些接口？
有哪些中间件？
有哪些配置？
```

都会围绕这个 `app` 组织。

注意这里变量为什么叫 `app`？

其实可以叫别的名字，但 `app` 是 Web 项目里非常常见的约定。

后面的 Uvicorn 命令也会用到这个变量名。

---

## 4.5 `@app.get("/")` 是什么？

```python
@app.get("/")
def home():
```

可以先把它读成人话：

> 当有人通过 **GET** 请求访问 `/` 时，请执行下面这个 `home()` 函数。

这里：

```text
GET
→ HTTP 请求方法

/
→ URL 路径，也就是网站根路径

home()
→ 真正执行的 Python 函数
```

`@app.get(...)` 这种以 `@` 开头的写法在 Python 中叫 **Decorator（装饰器）**。

现在不需要先学习装饰器全部语法。

你只要先理解它在 FastAPI 里的作用：

> **把一个 Python 函数注册成 HTTP 接口。**

---

## 4.6 `return {"message": ...}` 为什么浏览器看到的是 JSON？

我们的函数返回的是 Python 字典：

```python
{
    "message": "Hello Mini Agent"
}
```

FastAPI 会帮我们把它转换成 JSON HTTP 响应。

所以浏览器最后看到：

```json
{
  "message": "Hello Mini Agent"
}
```

这就是框架帮我们省掉的工作之一。

---

## 4.7 启动服务器

回到项目根目录：

```bash
pwd
```

应该是：

```text
/home/yourname/mini--mm-agent
```

执行：

```bash
uvicorn app.main:app --reload --port 8001
```

正常应该看到类似：

```text
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Started reloader process ...
INFO:     Started server process ...
INFO:     Application startup complete.
```

**这个 Terminal 暂时不要关。**

因为 Uvicorn 正在这个终端里运行服务器。

如果你按：

```text
Ctrl + C
```

服务器就会停止。

---

## 4.8 `uvicorn app.main:app --reload --port 8001` 怎么读？

第一次看到很像一串咒语，我们拆开：

```text
uvicorn
→ 使用 Uvicorn 启动服务器

app.main
→ 找到 app/main.py 这个 Python 模块

:app
→ 在这个模块里找到名叫 app 的变量

--reload
→ 代码保存后自动重新加载开发服务器

--port 8001
→ 监听 8001 端口
```

所以整句话翻译成人话就是：

> 使用 Uvicorn 启动 `app/main.py` 中的 `app = FastAPI()`，开发时监控代码变化，并在 8001 端口提供服务。

---

## 4.9 `127.0.0.1` 和 `8001` 是什么？

地址：

```text
http://127.0.0.1:8001
```

可以粗略拆成：

```text
127.0.0.1
→ 当前电脑自己，也常叫 localhost

8001
→ 这个程序使用的端口
```

一台电脑可以同时运行很多网络程序，所以需要端口区分：

```text
程序 A → 8001
程序 B → 3000
程序 C → 其他端口
```

后面我们的前端会使用 3000，后端使用 8001。

---

## 4.10 用 Windows 浏览器访问 WSL 中的服务

虽然 Uvicorn 是在 WSL Ubuntu 中运行的，你通常仍然可以直接在 Windows 浏览器打开：

```text
http://127.0.0.1:8001
```

应该看到：

```json
{"message":"Hello Mini Agent"}
```

恭喜：现在已经发生了第一次真正的 HTTP 调用。

```text
Windows 浏览器
↓ HTTP GET
WSL 中的 Uvicorn
↓
FastAPI
↓
home()
↓
JSON
↓
浏览器
```

---

## 4.11 再打开 `/docs`

访问：

```text
http://127.0.0.1:8001/docs
```

你会看到 FastAPI 自动生成的 Swagger UI。

里面应该出现：

```text
GET /
```

这个页面非常重要。

因为后面我们创建 POST 接口以后，不用一开始就写前端，可以直接在 `/docs` 中测试接口。

---

## 4.12 常见错误 1：`Address already in use`

如果启动时看到：

```text
[Errno 98] Address already in use
```

翻译成人话：

> 8001 端口已经被另一个进程占用了。

查看是谁占用：

```bash
ss -ltnp | grep :8001
```

也可以临时换一个：

```bash
uvicorn app.main:app --reload --port 8002
```

那浏览器也要改成：

```text
http://127.0.0.1:8002
```

---

## 4.13 常见错误 2：`Attribute "app" not found`

如果看到类似：

```text
Error loading ASGI app. Attribute "app" not found in module "app.main".
```

先检查：

```python
app = FastAPI()
```

是不是已经保存到 `app/main.py`。

如果 VSCode 标签上还有小圆点，很可能你只是改了编辑器内容，却还没 `Ctrl + S`。

---

## 4.14 本章小练习：自己增加一个 GET 接口

在下面继续增加：

```python
@app.get("/hello")
def hello():
    return {
        "message": "Hello from /hello"
    }
```

保存以后访问：

```text
http://127.0.0.1:8001/hello
```

再去：

```text
http://127.0.0.1:8001/docs
```

看看是不是出现两个 GET 接口。

练习完成后，你可以保留 `/hello`，也可以删掉它。

### 本章检查清单

```text
[ ] pip 安装 fastapi 和 uvicorn 成功
[ ] uvicorn 能启动
[ ] 浏览器访问 / 能看到 JSON
[ ] /docs 能打开
[ ] 能解释 app.main:app
[ ] 能自己新增一个 GET 路由
```

### 你现在应该能回答

> 为什么我们已经写了 FastAPI，还需要 Uvicorn？

---

# 第 5 章：GET、POST、Header 和 JSON —— 前端到底怎样把数据交给后端？

> **本章目标**：理解 HTTP 请求最关键的几部分，并写出第一个接收 JSON 的 POST API。  
> **完成效果**：能用 Swagger 和 curl 向 `/responses` 发送 JSON，并拿到后端返回值。  
> **核心知识**：GET、POST、URL、Header、Body、JSON、Pydantic、HTTP 状态码。

这一章非常重要。

因为后面的：

```text
前端调用你的 FastAPI
你的 FastAPI 调用 Responses API
Agent 把结果返回前端
```

底层都离不开 HTTP 数据交换。

我们这一章暂时**还不调用大模型**。

先把 HTTP 本身搞懂。

---

## 5.1 为什么浏览器地址栏可以直接访问 GET？

当你在地址栏输入：

```text
http://127.0.0.1:8001/
```

然后按回车，浏览器默认会发送类似：

```text
GET /
```

而你的代码刚好有：

```python
@app.get("/")
```

所以匹配成功。

GET 通常用于：

```text
读取页面
获取资源
查询数据
```

例如以后可能看到：

```text
GET /users/123
GET /projects/abc
GET /status
```

---

## 5.2 为什么聊天请求更适合 POST？

假设用户想发送：

```text
你好，请解释什么是 Agent
```

我们希望把它作为结构化数据提交：

```json
{
  "input": "你好，请解释什么是 Agent"
}
```

这种“把一份数据交给服务器处理”的场景通常使用 POST。

所以可以先这样记：

```text
GET
→ 我想获取东西

POST
→ 我想提交一份数据，让服务器处理
```

这不是 HTTP 的全部规则，但作为初学者第一层理解非常够用。

---

## 5.3 一个 HTTP 请求可以先想成四部分

以后看到任何 API，请先找这四个东西：

```text
1. Method
   GET / POST / PUT / DELETE ...

2. URL
   http://127.0.0.1:8001/responses

3. Headers
   Content-Type: application/json

4. Body
   {"input":"你好"}
```

这四个概念后面会反复出现。

---

## 5.4 先让 Python 描述“我希望收到什么数据”

打开：

```text
app/main.py
```

在顶部增加：

```python
from pydantic import BaseModel
```

然后定义：

```python
class ResponseRequest(BaseModel):
    input: str
```

现在 `app/main.py` 可以写成：

```python
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class ResponseRequest(BaseModel):
    input: str


@app.get("/")
def home():
    return {
        "message": "Hello Mini Agent"
    }


@app.post("/responses")
def create_response(request: ResponseRequest):
    return {
        "output": f"你输入了：{request.input}"
    }
```

保存。

因为上一章使用了：

```text
--reload
```

Uvicorn 通常会自动重新加载。

---

## 5.5 `BaseModel` 到底在做什么？

```python
class ResponseRequest(BaseModel):
    input: str
```

这段代码是在告诉 FastAPI：

> `/responses` 的请求 Body 应该是一个对象，其中必须有 `input` 字段，而且 `input` 应该是字符串。

也就是说它期待：

```json
{
  "input": "你好"
}
```

而不是：

```json
{
  "abc": "你好"
}
```

Pydantic 会帮助 FastAPI：

```text
解析 JSON
↓
检查字段
↓
检查类型
↓
转换成 Python 对象
```

于是你的函数里可以直接写：

```python
request.input
```

拿到用户提交的文字。

---

## 5.6 `@app.post("/responses")` 是什么？

```python
@app.post("/responses")
def create_response(request: ResponseRequest):
```

翻译成人话：

> 当有人通过 POST 请求访问 `/responses`，并且 Body 符合 `ResponseRequest` 格式时，执行 `create_response()`。

所以现在服务器有两个不同接口：

```text
GET /

POST /responses
```

它们即使都在同一个 FastAPI 程序里，作用完全不同。

---

## 5.7 为什么现在只是“复读”，不直接接大模型？

我们先写：

```python
return {
    "output": f"你输入了：{request.input}"
}
```

例如用户提交：

```text
你好
```

返回：

```json
{
  "output": "你输入了：你好"
}
```

它当然还不是 AI。

但这样我们可以先验证：

```text
HTTP POST
↓
JSON Body
↓
FastAPI
↓
Pydantic
↓
Python 函数
↓
JSON Response
```

这条链路独立是好的。

下一阶段再把中间的“复读”替换成真正模型调用。

这就是前面说的**逐层验证**。

---

## 5.8 用 Swagger 测试 POST

打开：

```text
http://127.0.0.1:8001/docs
```

现在应该看到：

```text
GET  /
POST /responses
```

展开：

```text
POST /responses
```

点击：

```text
Try it out
```

输入：

```json
{
  "input": "你好，我正在学习 Agent"
}
```

点击：

```text
Execute
```

正常应该得到状态码：

```text
200
```

Response body 类似：

```json
{
  "output": "你输入了：你好，我正在学习 Agent"
}
```

### `200` 是什么？

这是 HTTP Status Code（状态码）。

现在先认识几个最常见的：

```text
200
→ 请求成功

404
→ 资源或路径没找到

405
→ 路径可能存在，但 HTTP Method 不允许

422
→ FastAPI 收到请求，但数据格式没有通过验证

500
→ 服务器内部代码发生错误
```

以后看到报错时，状态码本身就是第一条线索。

---

## 5.9 为什么直接在浏览器地址栏打开 `/responses` 会报错？

试着在地址栏输入：

```text
http://127.0.0.1:8001/responses
```

你可能看到：

```json
{
  "detail": "Method Not Allowed"
}
```

或者状态码：

```text
405
```

原因不是 `/responses` 不存在。

而是：

```text
浏览器地址栏
默认发送 GET

你的接口
只接受 POST
```

也就是：

```text
GET /responses   ❌
POST /responses  ✅
```

这是一条非常重要的调试思路：

> **URL 对了，不代表 Method 就对了。**

---

## 5.10 不用 Swagger，使用 curl 发送请求

保持 Uvicorn 的 Terminal 继续运行。

在 VSCode 里**新开第二个 Terminal**。

如果新 Terminal 没自动激活 `.venv`，对 curl 没关系，因为 curl 不是 Python 包。

执行：

```bash
curl -X POST http://127.0.0.1:8001/responses \
  -H "Content-Type: application/json" \
  -d '{"input":"你好，我是从终端发过来的"}'
```

正常应该看到：

```json
{"output":"你输入了：你好，我是从终端发过来的"}
```

---

## 5.11 把 curl 一段一段拆开

完整命令：

```bash
curl -X POST http://127.0.0.1:8001/responses \
  -H "Content-Type: application/json" \
  -d '{"input":"你好"}'
```

### `curl`

它是一个命令行 HTTP 客户端。

可以理解成：

> 不通过浏览器页面，直接从 Terminal 手工发送 HTTP 请求。

### `-X POST`

```text
-X
→ 指定 HTTP Method

POST
→ 本次使用 POST
```

### URL

```text
http://127.0.0.1:8001/responses
```

告诉 curl：

> 请求发给谁。

### `-H "Content-Type: application/json"`

`-H` 用来增加 HTTP Header。

这里告诉 FastAPI：

> 我发送的 Body 是 JSON 格式。

### `-d ...`

```bash
-d '{"input":"你好"}'
```

`-d` 是真正发送的数据。

这里就是 HTTP Body。

---

## 5.12 Header 和 Body 可以怎么理解？

可以做一个不完全严谨、但很好记的类比。

假设你寄一个包裹：

```text
快递单上的说明
→ Header

包裹里面真正的东西
→ Body
```

例如：

```text
Content-Type: application/json
```

是在告诉服务器：

> “请按 JSON 的方式理解里面的数据。”

真正的数据则是：

```json
{
  "input": "你好"
}
```

---

## 5.13 JSON 和 Python 字典看起来为什么这么像？

Python 字典：

```python
{
    "input": "你好"
}
```

JSON 文本：

```json
{
  "input": "你好"
}
```

肉眼非常像。

但它们不是同一种东西。

Python 字典是：

```text
Python 进程里的对象
```

JSON 是：

```text
一种跨程序传输数据的文本格式
```

以后你会看到：

```python
json.dumps(...)
```

把 Python 对象变成 JSON 字符串；

以及：

```python
json.loads(...)
```

把 JSON 字符串解析成 Python 对象。

现在只需要先把这个区别记住。

---

## 5.14 故意发送一个错误请求，看看 Pydantic 怎么保护接口

在 `/docs` 中把请求改成：

```json
{
  "abc": "你好"
}
```

但我们的模型要求：

```python
class ResponseRequest(BaseModel):
    input: str
```

也就是说 `input` 是必需的。

所以 FastAPI 会拒绝请求，通常返回：

```text
422 Unprocessable Entity
```

这说明一个很重要的事情：

> 你的 `create_response()` 函数甚至不需要自己手写 `if input 不存在`，Pydantic 已经在请求进入业务函数之前帮你做了一层数据验证。

---

## 5.15 常见错误：把 `-X` 写成 `-x`

错误：

```bash
curl -x POST ...
```

你可能得到：

```text
Could not resolve proxy: POST
```

原因是 curl 中：

```text
-x
→ proxy，设置代理

-X
→ request method，指定 HTTP 方法
```

所以必须注意大小写：

```bash
-X POST
```

---

## 5.16 这一章和以后前端有什么关系？

未来 JavaScript 会写：

```javascript
fetch("http://127.0.0.1:8001/responses", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        input: "你好"
    })
})
```

你现在不需要学 JavaScript。

只要先发现它和 curl 的对应关系：

```text
curl -X POST
↔ method: "POST"

curl -H
↔ headers

curl -d
↔ body
```

本质上它们都在构造同一个 HTTP 请求。

---

## 5.17 这一章和以后调用大模型又有什么关系？

下一阶段你的程序会变成：

```text
浏览器 / Swagger / curl
        ↓ POST JSON
你的 FastAPI
        ↓ 网络 API 请求
Responses API
        ↓
大模型
```

也就是说：

> **前端调用你的后端，和你的后端调用模型服务，本质上都是程序之间通过 API 交换数据。**

理解这一层以后，后面的模型 API 就不会显得那么神秘。

---

## 5.18 本章小练习

给请求模型再增加一个字段：

```python
class ResponseRequest(BaseModel):
    input: str
    user_name: str
```

然后让返回值变成类似：

```json
{
  "output": "乐知，你输入了：你好"
}
```

尝试自己修改 Swagger 请求 JSON。

练习完后，为了和后续教程保持一致，可以把代码恢复为：

```python
class ResponseRequest(BaseModel):
    input: str
```

### 本章检查清单

```text
[ ] 能解释 GET 和 POST 的第一层区别
[ ] 知道 URL / Header / Body 分别是什么
[ ] 能用 Swagger 发送 POST
[ ] 能用 curl 发送 POST JSON
[ ] 知道浏览器地址栏为什么不能直接测试 POST
[ ] 知道 200 / 405 / 422 / 500 大概代表什么
[ ] 知道 BaseModel 在帮我们验证请求数据
```

### 你现在应该能回答

如果看到下面这条请求：

```bash
curl -X POST http://127.0.0.1:8001/responses \
  -H "Content-Type: application/json" \
  -d '{"input":"你好"}'
```

你应该能指出：

```text
HTTP Method 在哪里？
URL 在哪里？
Header 在哪里？
Body 在哪里？
```

如果这些都能自己解释，第 1～5 章的 Web 基础已经真正打通。

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