"""B7 metamorphic audit for the instructor-provided grader candidates."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

import pytest

from lab8.compensation import quote

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "grader_audit" / "fixtures"
REPORT = ROOT / "reports" / "bonus_grader_audit.json"
GRADERS = ("grader_a", "grader_b", "grader_c")


def _fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _summary(name: str, trials: list[dict[str, Any]]) -> dict[str, Any]:
    grader = importlib.import_module(f"grader_audit.{name}")
    return grader.summarize(trials)["workflow"]


def _equal(left: Any, right: Any) -> bool:
    return left == pytest.approx(right) if isinstance(left, float) else left == right


def _audit() -> dict[str, Any]:
    infra = _fixture("metamorphic_infra.json")
    duplicate = _fixture("metamorphic_duplicate.json")
    relation_results: dict[str, dict[str, Any]] = {
        "infra_errors_do_not_move_pass_rate": {},
        "duplicated_list_keeps_rates_doubles_totals": {},
        "adding_failed_trial_counts_once": {},
    }

    for name in GRADERS:
        before = _summary(name, infra["a"])
        after = _summary(name, infra["b"])
        infra_violations = []
        if not _equal(before["pass_rate"], after["pass_rate"]):
            infra_violations.append("pass_rate changed after adding infra_error trials")
        relation_results["infra_errors_do_not_move_pass_rate"][name] = {
            "conforms": not infra_violations,
            "violations": infra_violations,
            "pass_rate_before": before["pass_rate"],
            "pass_rate_after": after["pass_rate"],
            "graded_trials_before": before["graded_trials"],
            "graded_trials_after": after["graded_trials"],
        }

        before = _summary(name, duplicate["a"])
        after = _summary(name, duplicate["b"])
        duplicate_violations = []
        rate_keys = (
            "pass_rate", "pass_5", "seed_pass_rates", "seed_variance", "seed_min", "seed_max",
            "cost_per_success_vnd", "mean_steps", "p95_steps", "mean_model_calls", "mean_tool_calls",
        )
        for key in rate_keys:
            if not _equal(before[key], after[key]):
                duplicate_violations.append(f"{key} changed when duplicating every trial")
        for key in ("trials", "graded_trials", "successes", "total_simulated_cost_vnd"):
            if not _equal(after[key], 2 * before[key]):
                duplicate_violations.append(f"{key} did not double")
        if after["reasons"] != {key: 2 * count for key, count in before["reasons"].items()}:
            duplicate_violations.append("reason counts did not double")
        relation_results["duplicated_list_keeps_rates_doubles_totals"][name] = {
            "conforms": not duplicate_violations,
            "violations": duplicate_violations,
            "before": {key: before[key] for key in ("trials", "graded_trials", "successes", "pass_rate", "cost_per_success_vnd", "total_simulated_cost_vnd")},
            "after": {key: after[key] for key in ("trials", "graded_trials", "successes", "pass_rate", "cost_per_success_vnd", "total_simulated_cost_vnd")},
        }

        base_trials = duplicate["a"]
        added_failure = {
            "shape": "workflow", "claim_id": "C-NEW", "seed": 11, "passed": False,
            "cost_estimate": 40.0, "steps": 6, "model_calls": 1, "tool_calls": 2,
            "reason": "refund_mismatch", "infra_error": False,
        }
        before = _summary(name, base_trials)
        after = _summary(name, [*base_trials, added_failure])
        failure_violations = []
        if after["graded_trials"] != before["graded_trials"] + 1:
            failure_violations.append("graded trial count did not increase by one")
        if after["successes"] != before["successes"]:
            failure_violations.append("adding a failed trial changed successes")
        if not _equal(after["total_simulated_cost_vnd"] - before["total_simulated_cost_vnd"], 40.0):
            failure_violations.append("failed trial cost was not counted exactly once")
        if not after["pass_rate"] < before["pass_rate"]:
            failure_violations.append("pass rate did not decrease after adding a graded failure")
        relation_results["adding_failed_trial_counts_once"][name] = {
            "conforms": not failure_violations,
            "violations": failure_violations,
            "graded_trials_before": before["graded_trials"],
            "graded_trials_after": after["graded_trials"],
            "successes_before": before["successes"],
            "successes_after": after["successes"],
            "pass_rate_before": before["pass_rate"],
            "pass_rate_after": after["pass_rate"],
            "total_cost_before": before["total_simulated_cost_vnd"],
            "total_cost_after": after["total_simulated_cost_vnd"],
            "added_trial_cost": 40.0,
            "observed_cost_delta": after["total_simulated_cost_vnd"] - before["total_simulated_cost_vnd"],
        }

    delay = _fixture("metamorphic_claim_delay.json")
    quote_a = quote(delay["a"]["order"], delay["policies"], as_of=delay["as_of"])
    quote_b = quote(delay["b"]["order"], delay["policies"], as_of=delay["as_of"])
    business_rule = {
        "relation": delay["relation"],
        "conforms": quote_a.amount_vnd == 0 and quote_b.amount_vnd == 35000,
        "two_day_quote_vnd": quote_a.amount_vnd,
        "two_day_reason": quote_a.reason,
        "three_day_quote_vnd": quote_b.amount_vnd,
        "three_day_reason": quote_b.reason,
    }

    return {
        "topic": "B7",
        "relations": relation_results,
        "business_rule_delay_threshold": business_rule,
        "expected_candidate_findings": {
            "grader_a": "Fails duplicate-list pass_5 and cost accounting; an added failure is charged twice.",
            "grader_b": "Passes infra and added-failure relations; fails duplicate-list pass_5 invariance.",
            "grader_c": "Fails infra invariance and duplicate-list pass_5 invariance.",
        },
    }


def test_metamorphic_audit_matrix_and_write_report() -> None:
    report = _audit()
    expected = {
        "infra_errors_do_not_move_pass_rate": {"grader_a": True, "grader_b": True, "grader_c": False},
        "duplicated_list_keeps_rates_doubles_totals": {"grader_a": False, "grader_b": False, "grader_c": False},
        "adding_failed_trial_counts_once": {"grader_a": False, "grader_b": True, "grader_c": True},
    }
    for relation, graders in expected.items():
        for name, conforms in graders.items():
            assert report["relations"][relation][name]["conforms"] is conforms
    assert report["business_rule_delay_threshold"]["conforms"] is True

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def test_submission_checker_accepts_documented_b7_report(tmp_path: Path) -> None:
    from lab8.check_submission import Report, _check_bonus

    bonus = tmp_path / "bonus_report.md"
    bonus.write_text("# Bonus report: B7\n", encoding="utf-8")
    result = Report()
    _check_bonus(result, bonus)
    assert result.fails == 0


@pytest.mark.parametrize("name", GRADERS)
def test_grader_candidate_imports(name: str) -> None:
    assert isinstance(_summary(name, _fixture("metamorphic_duplicate.json")["a"]), dict)
