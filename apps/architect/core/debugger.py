import debugpy
import os

def setup_debugger():
    if os.environ.get("ENABLE_DEBUGGER") != "true":
        return
    try:
        debugpy.listen(("0.0.0.0", 5678))
    except RuntimeError:
        pass