# 第 17 章：把真实工具结果交回模型 —— `function_call_output` 到底在做什么？

> **本章目标**：完成“模型提出工具调用 → Python 执行 → 把真实结果交回模型”这一整条闭环。  
> **完成效果**：模型能够基于工具执行结果继续回答，而不是只停留在“我要调用某工具”。  
> **核心知识**：`response.output`、`function_call`、`call_id`、`function_call_output`、上下文继续。

上一章我们已经能真正执行工具。

例如模型返回：

```text
name = add_numbers
arguments = {"a":123,"b":456}
```

我们的 Python 执行：

```python
add_numbers(a=123, b=456)
```

得到：

```text
579
```

但这里还有一个关键问题：

> 模型并不知道我们的 Python 已经算出了 579。

所以必须把结果再交回模型。

---

## 17.1 为什么不能直接把 579 返回给用户？

对于特别简单的任务，确实可以。

例如用户问：

```text
123 + 456 等于多少？
```

工具得到：

```text
579
```

直接返回似乎没问题。

但复杂任务经常需要模型继续组织答案。

例如用户说：

```text
请获取服务器当前时间，
再告诉我距离整点还剩多少分钟，
最后用一句自然语言解释。
```

工具可能只返回：

```text
2026-09-11 10:42:18
```

这个结果并不是最终回答。

模型还需要：

```text
读取结果
↓
理解时间
↓
决定是否还要调用别的工具
↓
最后组织成自然语言
```

所以工具结果必须回到模型。

---

## 17.2 从 `response.output` 中找到 function call

Responses API 返回：

```python
response
```

其中：

```python
response.output
```

可能包含不同类型 item。

我们只找：

```python
item.type == "function_call"
```

代码：

```python
tool_calls = [
    item
    for item in response.output
    if item.type == "function_call"
]
```

这段列表推导式可以拆成更容易理解的版本：

```python
tool_calls = []

for item in response.output:
    if item.type == "function_call":
        tool_calls.append(item)
```

两种写法作用一样。

初学时如果觉得列表推导式太挤，先看第二种。

---

## 17.3 为什么是一组 `tool_calls`，不是单个 `tool_call`？

因为模型一轮可能提出多个工具调用。

例如：

```text
请告诉我服务器时间，
同时计算 88 + 99。
```

模型可能一轮输出：

```text
function_call #1 → get_server_time
function_call #2 → add_numbers
```

所以代码从一开始就按：

```python
for tool_call in tool_calls:
```

处理更合理。

---

## 17.4 `call_id` 是什么？

每次 `function_call` 都有自己的：

```python
tool_call.call_id
```

可以把它理解成：

> 这一次工具调用请求的编号。

例如模型一轮提出：

```text
call_001 → get_server_time
call_002 → add_numbers
```

当 Python 执行完以后，模型必须知道：

```text
10:52:30
```

对应哪个调用；

```text
187
```

又对应哪个调用。

这就是 `call_id` 的意义。

---

## 17.5 构造 `function_call_output`

执行工具：

```python
tool_result = await execute_tool(
    tool_call
)
```

然后构造：

```python
tool_outputs.append({
    "type": "function_call_output",
    "call_id": tool_call.call_id,
    "output": str(tool_result),
})
```

三个字段逐个看。

### `type`

```python
"type": "function_call_output"
```

告诉模型：

> 这是某次函数调用的执行结果。

### `call_id`

```python
"call_id": tool_call.call_id
```

告诉模型：

> 这个结果对应你刚才提出的哪次调用。

### `output`

```python
"output": str(tool_result)
```

是真正工具返回值。

例如：

```text
579
```

---

## 17.6 为什么把结果 `str(...)`？

不同 Python 工具可能返回：

```text
int
float
list
dict
自定义对象
字符串
```

Responses API 的 function output 最容易统一成文本表示。

所以教学版先：

```python
str(tool_result)
```

例如：

```python
579
```

变成：

```text
"579"
```

以后更复杂的项目可能统一返回 JSON，但当前这样最容易理解。

---

## 17.7 把工具结果再次发送给模型

工具结果准备好后：

```python
response = await create_model_response(
    tool_outputs,
    instructions=AGENT_INSTRUCTIONS,
    previous_response_id=response.id,
    tools=TOOL_DEFINITIONS,
)
```

这里一定要注意两个不同的 ID：

```text
response.id
```

和：

```text
call_id
```

它们不是一回事。

### `response.id`

表示：

> 上一轮模型 Response 的 ID。

下一次调用通过：

```python
previous_response_id=response.id
```

继续上一轮模型上下文。

### `call_id`

表示：

> 某一个具体 function call 的 ID。

它放在：

```python
function_call_output
```

中，把工具结果和对应调用匹配起来。

---

## 17.8 整条链现在是什么？

```text
用户
↓
Responses API
↓
function_call
name=add_numbers
arguments={a:123,b:456}
call_id=call_1
↓
Python execute_tool()
↓
579
↓
function_call_output
call_id=call_1
output="579"
↓
Responses API
↓
模型看到真实结果
↓
继续生成
```

这才是完整 Tool Calling。

只有：

```text
function_call
```

还不算闭环。

---

## 17.9 如果工具执行失败怎么办？

假设模型调用：

```text
run_python
```

但缺少：

```text
code
```

我们的 Executor 可以返回：

```text
工具 run_python 缺少必需参数 ['code']，请补齐参数后重新调用。
```

注意我们不一定要让整个 Agent 直接崩掉。

这个错误文本本身也可以作为：

```python
function_call_output
```

交回模型。

于是模型下一轮可能意识到：

```text
刚才参数错了
↓
重新生成 code 参数
↓
再次调用 run_python
```

这就是 Agent “观察错误并修正”的基础。

---

## 17.10 Tool 错误和程序错误要区分

例如：

```text
工具输入参数不对
```

有时可以作为工具结果交给模型继续处理。

但如果：

```text
数据库损坏
代码 Bug
整个 SDK 初始化失败
```

可能就应该：

```text
记录 ERROR
终止请求
返回 HTTP 500
```

真实 Agent 系统需要决定：

> 哪些错误可以让模型恢复，哪些错误必须终止。

教学版先建立这个意识即可。

---

## 17.11 测试时应该观察什么？

不要只看最终回答。

你更应该观察日志：

```text
模型提出哪个工具？
↓
arguments 是什么？
↓
Python 真正返回了什么？
↓
下一轮模型有没有继续？
```

因为 Agent 调试和普通聊天调试最大的区别之一就是：

> 你必须观察中间动作，而不能只观察最终一句话。

---

### 第 17 章检查清单

```text
[ ] 能从 response.output 找到 function_call
[ ] 知道一轮可能有多个 function_call
[ ] 知道 call_id 是具体工具调用 ID
[ ] 知道 response.id 是模型 Response ID
[ ] 能解释两种 ID 为什么不同
[ ] 会构造 function_call_output
[ ] 知道工具结果必须交回模型，模型才能继续
[ ] 知道部分工具错误也可以交回模型让它修正
```

### 本章小练习

让模型同时完成：

```text
获取服务器时间
+
计算 88 + 99
```

观察 `response.output` 是否出现多个 `function_call`。

如果模型只产生一个，也不一定是程序错误；不同模型的规划方式可能不同。

### 你现在应该能回答

> `response.id` 和 `tool_call.call_id` 分别用来解决什么问题？
