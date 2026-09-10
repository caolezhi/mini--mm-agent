"""Convenience launcher for beginners.

You can still start the app with:
    uvicorn app.main:app --reload --port 8001

Or simply:
    python main.py
"""

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
    )
