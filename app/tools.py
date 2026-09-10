from datetime import datetime

from app.sandbox import run_python


def get_server_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_numbers(a: float, b: float):
    return a + b


# Python side: map the tool name chosen by the model to a real function.
TOOL_REGISTRY = {
    "get_server_time": get_server_time,
    "add_numbers": add_numbers,
    "run_python": run_python,
}


# Model side: describe which tools exist and which parameters they require.
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "name": "get_server_time",
        "description": "获取运行当前程序的服务器当前时间",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "add_numbers",
        "description": "计算两个数字的加法",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "第一个数字",
                },
                "b": {
                    "type": "number",
                    "description": "第二个数字",
                },
            },
            "required": ["a", "b"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "run_python",
        "description": (
            "在隔离的E2B沙箱中执行Python代码。"
            "适合精确计算、数据处理和算法任务。"
            "调用时必须通过code参数提供完整可执行Python代码。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "需要执行的完整Python代码",
                }
            },
            "required": ["code"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]
