# Agent 核心章节精读

主 README 保留完整 20 章路线；这里把最关键的 **第 15～18 章**单独拆成更详细的初学者版本，方便逐章学习和反复查阅。

建议顺序：

1. [第 15 章：Tool Calling —— Chatbot 与 Agent 的分界线](15-tool-calling.md)
2. [第 16 章：Tool Registry —— Python 怎么找到真实函数](16-tool-registry.md)
3. [第 17 章：function_call_output —— 把真实工具结果交回模型](17-function-call-output.md)
4. [第 18 章：Agent Loop —— 整个 Agent 的心脏](18-agent-loop.md)

这四章对应一条完整主线：

```text
普通 Python 函数
↓
Tool Definition 告诉模型有哪些工具
↓
模型产生 function_call
↓
Tool Registry 找到真实 Python 函数
↓
Tool Executor 执行
↓
function_call_output 把结果交回模型
↓
模型再次判断
↓
Agent Loop 直到任务结束
```

配套图：

- [`tool-anatomy.svg`](../images/tool-anatomy.svg)：Python 函数、Tool Definition、function_call、Executor 的区别
- [`tool-calling-loop.svg`](../images/tool-calling-loop.svg)：Tool Calling 与 Agent Loop 的整体闭环
- [`agent-loop-steps.svg`](../images/agent-loop-steps.svg)：Agent Loop 每一轮发生了什么

学习要求不是“把最终代码背下来”，而是读完后能够回答：

```text
模型到底有没有执行函数？
Tool Definition 和 Registry 为什么是两套东西？
call_id 和 response.id 有什么区别？
为什么工具结果必须再回模型？
为什么 Agent Loop 一定需要停止条件？
```

如果这些问题能不看源码解释清楚，再进入 E2B Sandbox，会顺很多。
