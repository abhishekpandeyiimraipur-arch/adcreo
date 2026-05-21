# ci/validate_state_machine.py
# CI-A: validates the 22-state Adcreo FSM per [TDD-CICD]-A.
# Reads backend/state_transitions.yaml — fails on orphan states,
# illegal transitions, or wrong terminal state count.
# Exit 0 = green. Exit 1 = red.

import json
import sys
from pathlib import Path
import yaml

YAML_PATH = Path(__file__).resolve().parent.parent / "backend" / "state_transitions.yaml"
EXPECTED_STATE_COUNT = 22
EXPECTED_TERMINAL_STATES = {"export_ready", "failed_category", "failed_compliance"}


def load_yaml():
    if not YAML_PATH.exists():
        print(json.dumps({"error": f"Not found: {YAML_PATH}"}))
        sys.exit(1)
    with open(YAML_PATH) as f:
        return yaml.safe_load(f)


def validate(data):
    errors = []
    states = set(data["states"])
    transitions = data["transitions"]
    terminal_states = set(data["terminal_states"])

    # 1. State count
    if len(states) != EXPECTED_STATE_COUNT:
        errors.append(f"Expected {EXPECTED_STATE_COUNT} states, got {len(states)}")

    # 2. Terminal states match
    if terminal_states != EXPECTED_TERMINAL_STATES:
        errors.append(f"Terminal states mismatch: {terminal_states}")

    # 3. Every state has a transitions entry
    for state in states:
        if state not in transitions:
            errors.append(f"No transitions entry for state: {state}")

    # 4. Every transition target is a known state
    for state, targets in transitions.items():
        if state not in states:
            errors.append(f"Transition source unknown state: {state}")
        for target in targets:
            if target not in states:
                errors.append(f"Transition target unknown state: {target} (from {state})")

    # 5. Terminal states have no outbound transitions
    for terminal in terminal_states:
        if transitions.get(terminal):
            errors.append(f"Terminal state has outbound transitions: {terminal}")

    # 6. No state is unreachable (except queued — it's the entry point)
    reachable = {"queued"}
    changed = True
    while changed:
        changed = False
        for state in list(reachable):
            for target in transitions.get(state, []):
                if target not in reachable:
                    reachable.add(target)
                    changed = True
    unreachable = states - reachable
    if unreachable:
        errors.append(f"Unreachable states: {unreachable}")

    return errors


def main():
    data = load_yaml()
    errors = validate(data)

    if errors:
        for e in errors:
            print(json.dumps({"status": "error", "detail": e}))
        sys.exit(1)

    print(json.dumps({
        "status": "ok",
        "states": len(data["states"]),
        "transitions": len(data["transitions"]),
        "terminal_states": list(data["terminal_states"])
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
