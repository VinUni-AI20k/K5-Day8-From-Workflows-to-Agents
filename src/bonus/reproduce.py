"""One offline entry point to reproduce benchmark and B3 evidence."""
import subprocess
import sys


def main():
    commands = [
        ["lab8.smoke"],
        ["pytest", "-q", "-o", "addopts="],
        ["lab8.benchmark", "--shapes", "workflow,single,orchestrator,swarm", "--cases", "data/public_claims.jsonl",
         "--seeds", "11,22,33,44,55", "--out", "reports/benchmark.json"],
        ["lab8.crash_test", "--count", "20", "--out", "reports/crash.json"],
        ["lab8.benchmark", "--shapes", "workflow,swarm,swarm_verified", "--extra-shape",
         "swarm_verified=bonus.swarm_verified:run_claim", "--seeds", "11,22,33,44,55", "--out", "reports/bonus_public.json"],
        ["lab8.benchmark", "--shapes", "workflow,swarm,swarm_verified", "--extra-shape",
         "swarm_verified=bonus.swarm_verified:run_claim", "--cases", "bonus/cases.jsonl", "--world", "bonus/world.json",
         "--seeds", "11,22,33,44,55", "--out", "reports/bonus_adversarial.json"],
        ["bonus.evidence"],
    ]
    for command in commands:
        print("\n> python -m " + " ".join(command), flush=True)
        subprocess.run([sys.executable, "-m", *command], check=True)


if __name__ == "__main__":
    main()
