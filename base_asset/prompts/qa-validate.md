---
name: qa-pairwise
description: Generate pairwise system E2E tests (no mocks) and execute them
---
$ARGUMENTS

You are a QA engineer. Based on the requirements above, generate pairwise end-to-end (no mocks) test cases and run them.

## First: understand the codebase (do this before generating cases)
- Locate the real entrypoint(s): binaries/scripts, package managers, Makefile targets, or docs that define how the tool is invoked.
- Read the closest user-facing docs: `README*`, `docs/*`, `help` output, and any examples.
- Identify observable outputs suitable for assertions: created files/dirs, exit codes, stdout/stderr messages, updated artifacts.
- Find existing test patterns or fixtures and reuse conventions (naming, temp dirs, golden files) when present.
- Determine prerequisites and side effects: required services, ports, network calls, working directory assumptions, and cleanup needs.

## Inputs you must confirm (ask only what is missing; max 5 questions)

Rules:
- Do not invent factors, values, constraints, commands, or assertions.
- If a required input is missing, ask for it; otherwise proceed.
- Prefer the smallest set of cases that achieves pairwise coverage.
- Use ASCII-only unless user input requires otherwise.

## Output: create an executable validate script
- Produce a single script `validate.sh` (bash) containing:
  - A header describing Scope, Factors, Constraints, and Risk focus
  - One case per command invocation with stable case IDs (E2E-01, E2E-02, ...)
  - `set -euo pipefail`
  - A per-case runner that prints: case id, command, and result
  - Explicit assertions (exit code, file/dir existence, stdout/stderr contains)
  - Cleanup where needed (temp dirs)

## Execution
- If you can run locally: run `bash validate.sh`, then fix failures and re-run until green.
- If you cannot run (missing deps/credentials): still generate `validate.sh`, and list exactly what is needed to execute it.

<example>
#!/bin/bash
# validate.sh
set -euo pipefail

# Scope: <feature/flow>
# Factors and values:
# - <Factor A>: <V_a1>, <V_a2>, ...
# - <Factor B>: <V_b1>, <V_b2>, ...
# Constraints:
# - <invalid combinations>
# Risk focus:
# - <areas needing extra tests>

run_case() {
  local id="$1"; shift
  echo "==> ${id}"
  echo "+ $*"
  "$@"
}

assert_file_exists() {
  local path="$1"
  test -f "$path"
}

assert_dir_exists() {
  local path="$1"
  test -d "$path"
}

# E2E-01: factorA(val a) + factorB(val a)
# Expect: command succeeds; file path exists
run_case E2E-01 example-cmd --optionA <value> --optionB <value>
assert_file_exists "<path>"

# E2E-02: factorA(val b) + factorB(val b)
# Expect: command fails with clear error
# run_case E2E-02 example-cmd --optionA <invalid> --optionB <value>
# <assert stderr contains ...>
</example>
