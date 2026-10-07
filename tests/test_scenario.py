"""The whole flow, S1-S11, graded by the independent grader against the answer key.

The model replies are SIMULATED, so this proves the code's rules end to end, not the model's answers.
Meaning rows stay PENDING here (no judge verdict or sign-off for simulated text), so the grader exits 3,
never 1.
"""

import json
import subprocess
import sys

from conftest import SimulatedClient
from qa.dataset import ROOT
from qa.export import export_markdown
from qa.review import workspace_dataset
from qa.scenario import run_scenario
from qa.store import load_state


def test_the_simulated_scenario_passes_every_mechanical_check_of_the_key(tmp_path):
    state_file = tmp_path / "workspace.json"
    observed = {
        "mode": "simulated",
        "model": {"model": "simulated"},
        **run_scenario(SimulatedClient(), state_file),
    }
    observed_path, results = tmp_path / "observed.json", tmp_path / "RESULTS.md"
    observed_path.write_text(json.dumps(observed))
    grader = [
        sys.executable,
        "reference/grade.py",
        "--observed",
        str(observed_path),
        "--results",
        str(results),
    ]
    run = subprocess.run(grader, cwd=ROOT, capture_output=True, text=True)
    assert run.returncode == 3, run.stdout + run.stderr
    assert "'FAIL': 0" in run.stdout

    state = load_state(state_file)
    exported = export_markdown(state, workspace_dataset(state), "R5")
    assert "Approved by Product reviewer" in exported and "EXPORT-v2:p1 (version 3)" in exported
    assert "Q2. Is JSON export available?" in exported.split("## Unresolved")[1]
