# GitHub 截图清单

仓库已经包含概念流程图和一个静态界面示意图。正式发布教程时，最好再补 3 张你本地真实运行截图。

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

- `POST /responses`
- `POST /responses/stream`
- `POST /responses/reset`
- `POST /agent`

建议保存为：

```text
docs/images/swagger.png
```

## 2. Agent Tool Calling 日志

执行一个必须调用 `run_python` 的任务，例如：

```text
请使用 Python 工具计算 1 到 10000 所有整数的平方和
```

截图尽量包含：

```text
Agent step=1
执行工具 name=run_python ...
工具执行完成 ...
Agent step=2
```

建议保存为：

```text
docs/images/agent-log.png
```

截图前注意不要让 `.env`、API Key、Token 或其他秘密出现在画面里。

## 3. 最终网页

启动前端：

```bash
python3 -m http.server 3000 --directory frontend
```

打开：

```text
http://127.0.0.1:3000
```

输入一个真实任务，等 Agent 回答后截图，保存为：

```text
docs/images/final-ui.png
```

然后把 README 中的界面示意图替换为真实截图。
