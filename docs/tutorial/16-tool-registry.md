# 第 16 章：Tool Registry —— 模型说了工具名以后，Python 怎么真正找到函数？

> **本章目标**：让程序根据模型返回的工具名，自动找到并执行对应 Python 函数。  
> **完成效果**：不再写一大串 `if / elif`，而是通过 Registry + JSON 参数解析统一执行工具。  
> **核心知识**：Registry、`json.loads()`、`**kwargs`、参数校验、Tool Executor。

上一章模型已经会返回：

```text
name = add_numbers
arguments = {"a":123,"b":456}
```

现在新的问题是：

> 模型只是给了一个工具名字符串，Python 怎么知道该执行哪个函数？

---

## 16.1 最直接但不好的写法

你当然可以写：

```python
if tool_name == "get_server_time":
    result = get_server_time()
elif tool_name == "add_numbers":
    result = add_numbers(...)
elif tool_name == "run_python":
    result = run_python(...)
```

工具只有两个时还能接受。

但以后工具可能有：

```text
10 个
30 个
100 个
```

那么：

```text
if / elif / elif / elif ...
```

会越来越难维护。

所以我们需要 **Tool Registry**。

---

## 16.2 Registry 本质上就是一个 Python 字典

在 `app/tools.py`：

```python
TOOL_REGISTRY = {
    "get_server_time": get_server_time,
    "add_numbers": add_numbers,
    "run_python": run_python,
}
```

注意右边没有括号：

```python
"add_numbers": add_numbers
```

而不是：

```python
"add_numbers": add_numbers()
```

为什么？

因为我们现在不是立刻执行函数，而是把**函数对象本身**存进字典。

可以做一个小实验：

```python
function = TOOL_REGISTRY["add_numbers"]

print(function)
print(function(a=10, b=20))
```

第二行最终会得到：

```text
30
```

所以 Registry 的本质非常朴素：

```text
工具名字符串
↓
找到真正 Python 函数对象
```

---

## 16.3 为什么模型的 arguments 还不能直接拿来调用？

模型返回的：

```python
tool_call.arguments
```

通常是 JSON 字符串。

例如：

```python
'{"a": 123, "b": 456}'
```

注意它是：

```text
str
```

而不是 Python `dict`。

所以要：

```python
import json


tool_arguments = json.loads(
    tool_call.arguments or "{}"
)
```

现在：

```python
tool_arguments
```

才变成：

```python
{
    "a": 123,
    "b": 456,
}
```

这和第 14 章的：

```python
json.dumps(...)
```

正好是反方向。

```text
json.dumps
Python 对象 → JSON 字符串

json.loads
JSON 字符串 → Python 对象
```

---

## 16.4 `**tool_arguments` 到底是什么？

现在：

```python
tool_arguments = {
    "a": 123,
    "b": 456,
}
```

执行：

```python
tool_function(**tool_arguments)
```

等价于：

```python
tool_function(
    a=123,
    b=456,
)
```

如果 `tool_function` 恰好是：

```python
add_numbers
```

那就相当于：

```python
add_numbers(
    a=123,
    b=456,
)
```

所以 `**` 在这里把字典展开成函数的关键字参数。

---

## 16.5 写一个统一的 Tool Executor

最终项目中，Tool Executor 在：

```text
app/services/agent_service.py
```

核心结构：

```python
async def execute_tool(tool_call):
    tool_name = tool_call.name

    tool_arguments = json.loads(
        tool_call.arguments or "{}"
    )

    tool_function = TOOL_REGISTRY.get(
        tool_name
    )

    if tool_function is None:
        return f"未知工具：{tool_name}"

    result = await asyncio.to_thread(
        tool_function,
        **tool_arguments,
    )

    return result
```

它解决四件事：

```text
① 读模型选择的工具名
② 把 JSON arguments 解析成 Python dict
③ 从 Registry 找真实 Python 函数
④ 调用函数并拿到结果
```

这就是一个最小的 **Tool Executor**。

---

## 16.6 为什么用 `.get()` 而不是直接 `TOOL_REGISTRY[tool_name]`？

如果写：

```python
TOOL_REGISTRY[tool_name]
```

模型返回一个不存在的名字时，会抛：

```text
KeyError
```

而：

```python
TOOL_REGISTRY.get(tool_name)
```

找不到时会返回：

```python
None
```

于是我们可以自己处理：

```python
if tool_function is None:
    return f"未知工具：{tool_name}"
```

Agent 系统一个很重要的思想就是：

> 模型输出不是永远完美的，Executor 应该有防御性。

---

## 16.7 为什么还要检查“缺少必需参数”？

Tool Definition 虽然写了：

```python
"required": ["a", "b"]
```

但现实里可能有：

- 第三方兼容 API 没严格实现 schema；
- 模型偶尔输出异常；
- Tool 定义写错；
- 参数解析出问题。

所以最终项目又加了一层 Python 侧校验：

```python
signature = inspect.signature(
    tool_function
)
```

它可以读取函数签名。

比如：

```python
def run_python(code: str):
    ...
```

Python 能知道它需要：

```text
code
```

于是如果模型返回：

```text
run_python arguments={}
```

我们不让整个程序立刻崩掉，而是返回：

```text
工具 run_python 缺少必需参数 ['code']
```

后面的 Agent Loop 可以把这个错误再交给模型，让模型修正。

---

## 16.8 为什么 Tool Executor 是 `async def`？

我们的工具函数目前本身是同步函数：

```python
def add_numbers(...)

def get_server_time(...)

def run_python(...)
```

其中 `run_python()` 会访问 E2B 网络服务，可能等待较久。

如果直接在异步 FastAPI Event Loop 中阻塞执行，可能影响其他请求。

所以最终项目使用：

```python
result = await asyncio.to_thread(
    tool_function,
    **tool_arguments,
)
```

可以先理解成：

> 把这个同步函数交给工作线程执行，异步事件循环不要一直被它卡住。

对 `add_numbers()` 来说其实没必要，但统一放在这套 Executor 里比较简单。

---

## 16.9 加日志确认“真的执行了工具”

在 Executor 中：

```python
logger.info(
    "执行工具 name=%s arguments=%s",
    tool_name,
    tool_arguments,
)
```

执行后：

```python
logger.info(
    "工具执行完成 name=%s result=%s",
    tool_name,
    result,
)
```

这样测试：

```text
请使用工具计算 123.5 + 456.8
```

你看到：

```text
执行工具 name=add_numbers arguments={'a': 123.5, 'b': 456.8}
工具执行完成 name=add_numbers result=580.3
```

就能确认：

> 不是模型嘴上说“我用了工具”，而是 Python Executor 真的执行了函数。

---

## 16.10 一个非常重要的安全问题

Tool Registry 代表：

```text
模型可以间接触发哪些 Python 能力
```

所以不要把任意危险函数都注册进去。

例如一个真实项目可能有：

```text
删除文件
转账
发送邮件
修改数据库
执行 Shell
```

这些工具都需要额外考虑：

```text
权限
用户确认
参数限制
审计日志
Sandbox
```

Tool Registry 不只是“代码组织”，它也是 Agent 权限边界的一部分。

---

### 第 16 章检查清单

```text
[ ] 知道 TOOL_REGISTRY 本质是 dict
[ ] 知道 Registry 存的是函数对象，不是函数返回值
[ ] 知道 tool_call.arguments 通常是 JSON 字符串
[ ] 会用 json.loads 转成 dict
[ ] 能解释 **tool_arguments
[ ] 知道未知工具要防御处理
[ ] 知道模型参数可能不完整
[ ] 知道 Tool Executor 是“真正执行动作”的地方
```

### 本章小练习

把上一章写的：

```python
multiply(a, b)
```

加入：

```python
TOOL_REGISTRY
```

然后手工执行：

```python
TOOL_REGISTRY["multiply"](
    a=6,
    b=7,
)
```

确认得到：

```text
42
```

### 你现在应该能回答

> Tool Definition 和 Tool Registry 分别是给谁用的？

一个完整回答：

```text
Tool Definition → 给模型看，帮助它选择工具并生成参数
Tool Registry → 给 Python 程序用，根据工具名找到真正函数
```
