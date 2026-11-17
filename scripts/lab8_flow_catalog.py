"""Documentation-only flow specifications, transcribed from the running code.

One catalog feeds Mermaid Markdown and offline SVG; no business code is imported
or executed. Rows/columns control the SVG layout, not the program's behavior.
"""

PALETTE = {
    "llm": ("MOCKLLM", "#eee6ff", "#7545ad"),
    "python": ("PYTHON", "#e5f3e9", "#247049"),
    "read": ("READ TOOL", "#e4f1ff", "#2d639f"),
    "host": ("HOST WRITER", "#fff0d7", "#9c6118"),
    "sqlite": ("SQLITE", "#e7ecf1", "#4b6277"),
    "result": ("KẾT QUẢ", "#eaf0d2", "#586728"),
    "crash": ("CRASH / EXCEPTION", "#ffe8e3", "#a34736"),
}


def n(id, title, kind, row, col=1, detail="", file="", decision=False):
    return dict(id=id, title=title, kind=kind, row=row, col=col,
                detail=detail, file=file, decision=decision)


def e(a, b, label="", back=False):
    return dict(source=a, target=b, label=label, back=back)


def p(id, title, nodes, edges, note=""):
    return dict(id=id, title=title, nodes=nodes, edges=edges, note=note)


def flow(id, title, input, steps, owner, output, difference, files, panels, notes):
    return dict(id=id, title=title, input=input, steps=steps, owner=owner,
                output=output, difference=difference, files=files, panels=panels, notes=notes)


T = "src/lab8/tools.py"
R = "src/lab8/runtime.py"
S = "src/lab8/shapes/workflow.py"
D = "src/lab8/durability.py"
P = "src/lab8/policy.py"
M = "src/lab8/mock_llm.py"
C = "src/lab8/shapes/common.py"
H = "src/lab8/handoff.py"
W = "src/lab8/shapes/workflow.py"
SA = "src/lab8/shapes/single.py"
O = "src/lab8/shapes/orchestrator.py"
SW = "src/lab8/shapes/swarm_reference.py"
B = "src/bonus/swarm_verified.py"
V = "src/bonus/verifier.py"
