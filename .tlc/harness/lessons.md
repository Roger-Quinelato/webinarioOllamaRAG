# Harness lessons

Auto-synced from gate failures; do not hand-edit.

Learned harness lessons (auto-synced; do not hand-edit):
- [stagnation/active/core] Identical validation fingerprint repeated. Change approach — do not re-apply the same failing edit.
  avoid: Do not retry the exact same patch, command, or suppression.
  prefer: Diagnose root cause with a different path, or escalate with BLOCKED / TRIED / NEED.
  before retrying: Diff your last edit against the gate output; ensure the next action is different.
- [ship/active/core] Ship claim without recent production PASS evidence. Produce real evidence before claiming done.
  avoid: Do not claim shipped based on unit tests alone when runtime paths changed.
  prefer: Run production E2E, write 90-verdict.txt PASS, cite the evidence path.
  before retrying: Confirm evidenceDir and a recent PASS verdict exist for this change.
- [empty-diff/active/core] Done/shipped was claimed with zero file changes. Either implement the work or explain why zero-diff is correct — do not claim shipped on an empty tree.
  avoid: Do not restate 'done' without a real diff or an explicit zero-change justification.
  prefer: Make the missing change, or clearly document why no files should change.
  before retrying: Inspect git status / changed files before the next stop.
- [lint/active/core] A lint gate failure means changed files still violate the project lint command. Fix the reported findings without suppressions.
  avoid: Do not add lint suppressions, disable comments, or delete failing files to silence the gate.
  prefer: Apply the smallest fix that clears each finding, then let the stop hook re-check.
  before retrying: Confirm the lint command targets only the intended changed files and still fails for the same codes.
- [test/active/core] A test gate failure means assertions still fail. Fix the behavior or the test under the real contract — do not delete or skip tests.
  avoid: Do not delete failing tests, mark them skipped, or weaken assertions to force green.
  prefer: Reproduce the failure, fix root cause, re-run the same test target.
  before retrying: Identify the failing test name/file from the gate output before editing.
_(1 more active lesson omitted under char budget)_
