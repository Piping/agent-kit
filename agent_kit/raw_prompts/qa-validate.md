---
name: qa-pairwise
description: Generate system e2e tests and execute it
---
$ARGUMENTS

Based on above requirement, you, as a QA engineer, generate pairwise end2end(no mocks) test cases.
<example>
#!/bin/bash
# Scope: <feature/flow>
# Factors and values:
# - <Factor A>: <V_a1>, <V_a2>, ...
# - <Factor B>: <V_b1>, <V_b2>, ...
# Constraints:
# - <invalid combinations>
# Risk focus:
# - <areas needing extra tests>

# E2E-01: factorA(val a) + factorB(val a)
# Expect: file path existed; command run without failture
exmaple-cmd --optionA --optionB

# E2E-02: factorA(val b) + factorB(val b)
# Expect: file path existed; command run without failture
exmaple-cmd --optionA --optionB
</example>

Guidrails:
- Keep cases minimal while ensuring full pairwise coverage.
- Ask questions until you have 95% confidence to do it right in oneshot
- Do not invent factors or values; ask for missing inputs.
- Make constraints explicit in the output notes.
- Use ASCII-only unless user input requires otherwise.
- Implement these e2e tests, map cases to real tool cli usage
- Run the tests or ask user to provide a validate.sh scripts, then run bash validate.sh and fix errors
