---
description: 代码 review
---
I want you to improve the quality of this codebase. To do this, install and run desloppify.
Run ALL of the following (requires Python 3.11+):

pip install --upgrade "desloppify[full]"
desloppify update-skill claude    # IMPORTANT — installs the workflow guide. Pick yours: claude, cursor, codex, copilot, windsurf, gemini
desloppify scan --path .
desloppify next

--path is the directory to scan (use "." for the whole project, or "src/" etc).

Your goal is to get the strict score that Desloppify produces as high as possible. Don't be lazy. Fix things properly
and fix things deep. Large refactors are fine if that's what it takes but also small fixes are great. The scoring is designed
to resist gaming, so the only way to improve it is to actually make the code better. Don't cheat.

Follow `next` — it tells you exactly what to fix, which file, and the resolve command to run
when done. Fix the issue, resolve it, run `next` again. Keep going until done.
Use `plan` to reorder priorities or cluster related issues.
You can scan to refresh things. The scan output includes agent instructions — follow them, don't augment with your own analysis but follow its plan.

最后用中文总结
$ARGUMENTS
