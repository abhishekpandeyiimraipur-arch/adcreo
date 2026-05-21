# tests/fsm/test_fsm_walk.py
# Unit tests for ci/validate_state_machine.py per [TDD-CICD]-B stage 2.

import pytest
import yaml
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "ci"))
from validate_state_machine import validate

YAML_PATH = Path(__file__).resolve().parent.parent.parent / "backend" / "state_transitions.yaml"


@pytest.fixture
def fsm():
    with open(YAML_PATH) as f:
        return yaml.safe_load(f)


def test_state_count(fsm):
    assert len(fsm["states"]) == 22


def test_no_validation_errors(fsm):
    errors = validate(fsm)
    assert errors == [], f"FSM validation errors: {errors}"


def test_terminal_states(fsm):
    assert set(fsm["terminal_states"]) == {
        "export_ready", "failed_category", "failed_compliance"
    }


def test_all_states_have_transitions(fsm):
    states = set(fsm["states"])
    transitions = fsm["transitions"]
    for state in states:
        assert state in transitions, f"Missing transitions for: {state}"


def test_terminal_states_have_no_outbound(fsm):
    for terminal in fsm["terminal_states"]:
        assert fsm["transitions"][terminal] == [], \
            f"Terminal state {terminal} has outbound transitions"


def test_legal_transition_queued_to_extracting(fsm):
    assert "extracting" in fsm["transitions"]["queued"]


def test_illegal_transition_queued_to_export_ready(fsm):
    assert "export_ready" not in fsm["transitions"]["queued"]


def test_failed_safety_can_retry(fsm):
    assert "scripting" in fsm["transitions"]["failed_safety"]


def test_failed_render_returns_to_strategy(fsm):
    assert "strategy_preview" in fsm["transitions"]["failed_render"]


def test_all_transition_targets_are_known_states(fsm):
    states = set(fsm["states"])
    for state, targets in fsm["transitions"].items():
        for target in targets:
            assert target in states, \
                f"Unknown target state: {target} (from {state})"
