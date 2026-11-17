"""Exercise exactly the source files copied by the v2 instructor grader."""
import os
from pathlib import Path
import subprocess
import sys


def test_three_shapes_run_against_pristine_host(tmp_path):
    repo = Path(__file__).resolve().parents[2]
    # Use the starter commit before this solution, even after solution commits.
    baseline = "034c6c4"
    files = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", baseline, "src/lab8", "src/config", "src/data"],
        cwd=repo, text=True,
    ).splitlines()
    for name in files:
        dest = tmp_path / name.removeprefix("src/")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(subprocess.check_output(["git", "show", f"{baseline}:{name}"], cwd=repo))
    for shape in ("workflow", "single", "orchestrator"):
        name = f"lab8/shapes/{shape}.py"
        (tmp_path / name).write_bytes((repo / "src" / name).read_bytes())
    code = '''
from pathlib import Path
from lab8.app import prepare_store
from lab8.shapes import SHAPES
from lab8.durability import InjectedCrash
for shape in ('workflow', 'single', 'orchestrator'):
    for claim, status, proposal in [('C-001','resolved',35000),('C-002','denied',0),('C-014','resolved',150000)]:
        store = Path(f'{shape}-{claim}.sqlite')
        prepare_store(store)
        result = SHAPES[shape](claim, seed=55, store_path=str(store))
        assert (result.status, result.proposal_amount) == (status, proposal)
        assert Path(result.trace_path).is_file()
    store = Path(f'{shape}-crash.sqlite')
    prepare_store(store)
    try:
        SHAPES[shape]('C-012', seed=55, store_path=str(store), crash_at='after_effect_before_checkpoint')
    except InjectedCrash:
        pass
    else:
        raise AssertionError('crash did not fire')
    result = SHAPES[shape]('C-012', seed=55, store_path=str(store))
    assert len(result.refund_effects) == result.committed_audit_count == 1
print('pristine host: all three shapes, seed 55, delta refund and crash recovery pass')
'''
    env = {**os.environ, "PYTHONPATH": str(tmp_path), "PYTHONUTF8": "1"}
    result = subprocess.run([sys.executable, "-c", code], cwd=tmp_path, env=env,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
