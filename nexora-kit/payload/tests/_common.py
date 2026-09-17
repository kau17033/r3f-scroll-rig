import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TOOLS = os.path.join(ROOT, "tools")
HOOKS = os.path.join(ROOT, ".claude", "hooks")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
