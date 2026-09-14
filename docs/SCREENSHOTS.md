# GitHub 截图清单

仓库已经包含统一风格的 SVG 概念图和静态界面示意图。正式公开教程时，最好再补 **3 张你本地真实运行截图**，让读者确认这些功能确实跑通。

> 截图前先检查画面里没有 `.env`、API Key、Token、Cookie 或其他秘密。

## 1. FastAPI `/docs`

启动后端：

```bash
uvicorn app.main:app --reload --port 8001
```

打开：

```text
http://127.0.0.1:8001/docs
```

截图中尽量包含：

- `GET /`
- `POST /responses`
- `POST /responses/stream`
- `POST /responses/reset`
- `POST /agent`

建议保存为：

```text
docs/images/swagger.png
```

这张图证明：

```text
FastAPI 路由已经完整加载
```

---

## 2. Agent Tool Calling / E2B 日志

执行一个必须调用 `run_python` 的任务，例如：

```text
请使用 Python 工具计算 1 到 10000 所有整数的平方和
```

截图尽量包含：

```text
Agent step=1
执行工具 name=run_python arguments={'code': '...'}
工具执行完成 name=run_python result=333383335000
Agent step=2
```

建议保存为：

```text
docs/images/agent-log.png
```

这张截图最重要的价值是证明：

```text
模型不是“嘴上说用了 Python”
而是真的产生 function_call
→ Python Executor
→ E2B
→ 真实工具结果
```

---

## 3. 最终网页

启动前端：

```bash
python3 -m http.server 3000 --directory frontend
```

打开：

```text
http://127.0.0.1:3000
```

建议截图时包含：

- `Mini Agent` 标题；
- `Session: xxxxxxxx`；
- `新会话` 按钮；
- 一个真实用户任务；
- Agent 的最终回答。

例如任务：

```text
请使用 Python 工具计算前 30 个斐波那契数，并告诉我第 30 个是多少
```

建议保存为：

```text
docs/images/final-ui.png
```

之后可以把主 README 中：

```markdown
![Mini Agent 最小前端示意](docs/images/final-ui-example.svg)
```

替换成真实截图：

```markdown
![Mini Agent 最终运行效果](docs/images/final-ui.png)
```

---

# 截图风格建议

为了让 GitHub 首页更整洁：

```text
浏览器截图尽量裁掉无关标签页
Terminal 不要截太多空白
统一使用浅色或统一深色主题
不要包含私人路径、密钥或账号信息
图像宽度尽量一致
```

概念图负责解释原理，真实截图负责证明项目真的跑通。两种图的作用不同，最好都保留。