from e2b_code_interpreter import Sandbox


def run_python(code: str):
    """Run model-generated Python inside an isolated E2B sandbox."""
    with Sandbox.create() as sandbox:
        execution = sandbox.run_code(code)

        if execution.error:
            return f"Python执行失败：{execution.error}"

        if execution.logs.stdout:
            return "\n".join(execution.logs.stdout)

        if execution.text:
            return execution.text

        return "代码执行成功，但没有输出。"
