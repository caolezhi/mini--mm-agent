# Mini Agent 深度教程

主 `README.md` 保留完整 20 章学习主线；这里把最关键、最容易产生“我会运行但其实没理解”的章节拆成更详细版本，适合逐章学习和反复查阅。

目前深度章节覆盖 **第 15～20 章**：

1. [第 15 章：Tool Calling —— Chatbot 与 Agent 的分界线](15-tool-calling.md)
2. [第 16 章：Tool Registry —— Python 怎么找到真实函数](16-tool-registry.md)
3. [第 17 章：function_call_output —— 把真实工具结果交回模型](17-function-call-output.md)
4. [第 18 章：Agent Loop —— 整个 Agent 的心脏](18-agent-loop.md)
5. [第 19 章：E2B Sandbox —— 为什么模型代码不能直接在服务器执行](19-e2b-sandbox.md)
6. [第 20 章：最小网页与完整端到端串联](20-frontend-e2e.md)

这六章对应一条完整主线：

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
function_call_output 把真实结果交回模型
↓
模型再次判断
↓
Agent Loop 直到任务结束
↓
run_python 把通用代码执行放进 E2B Sandbox
↓
FastAPI /agent 暴露成 HTTP API
↓
浏览器 fetch() 调用
↓
最终回答显示在页面
```

## 配套图

- [`tool-anatomy.svg`](../images/tool-anatomy.svg)：Python 函数、Tool Definition、function_call、Executor 的区别
- [`tool-calling-loop.svg`](../images/tool-calling-loop.svg)：Tool Calling 与 Agent Loop 的整体闭环
- [`agent-loop-steps.svg`](../images/agent-loop-steps.svg)：Agent Loop 每一轮发生了什么
- [`sandbox-boundary.svg`](../images/sandbox-boundary.svg)：为什么模型生成代码要进入 Sandbox
- [`frontend-e2e.svg`](../images/frontend-e2e.svg)：从网页到 Agent、Tool、E2B 再回网页的端到端流程

## 推荐学习方式

不要连续快速浏览六章。

每章都至少做三件事：

```text
1. 自己运行代码
2. 不看答案解释关键概念
3. 完成章节末尾的小练习
```

学习要求不是“把最终代码背下来”，而是读完后能够回答：

```text
模型到底有没有执行函数？
Tool Definition 和 Registry 为什么是两套东西？
call_id 和 response.id 有什么区别？
为什么工具结果必须再回模型？
为什么 Agent Loop 一定需要停止条件？
为什么 run_python 需要 Sandbox？
浏览器点击发送以后，请求到底经过哪些模块？
```

如果这些问题能不看源码解释清楚，再去阅读更大的 Agent 项目会顺很多。