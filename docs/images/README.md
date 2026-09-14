# 教程图片

这些 SVG 图片用于主 README 和详细教程章节的概念讲解：

- `agent-workflow.svg`：Mini Agent 总体工作流程
- `request-flow.svg`：一次 HTTP / Agent 请求的流动过程
- `project-structure.svg`：项目模块和职责
- `streaming-sse.svg`：Responses API Streaming → FastAPI → SSE → 客户端
- `tool-anatomy.svg`：Python 函数、Tool Definition、function_call、Executor 的关系
- `tool-calling-loop.svg`：Tool Calling 与 Agent Loop 的整体闭环
- `agent-loop-steps.svg`：Agent Loop 每一轮发生什么
- `sandbox-boundary.svg`：为什么模型生成的代码要放进隔离 Sandbox
- `frontend-e2e.svg`：浏览器 → FastAPI → Agent → Tool → E2B → 浏览器的完整端到端流程
- `final-ui-example.svg`：最小前端界面示意

统一风格：

```text
白色 / 极浅背景
圆角卡片
柔和蓝 / 绿 / 紫 / 黄配色
简洁图标
清晰箭头
尽量少的装饰元素
优先表达逻辑关系
```

图片使用 SVG，方便直接在 GitHub README 中显示，也方便后续修改文字、箭头和布局。