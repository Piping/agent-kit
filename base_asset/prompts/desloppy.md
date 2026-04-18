---
description: code review & refactor
---
I want you to improve the quality of this codebase. To do this, install and run desloppify.
Run ALL of the following (requires Python 3.11+):

pip install --upgrade "desloppify[full]"

Before scanning, check for directories that should be excluded (vendor, build output,
generated code, worktrees, etc.) and exclude obvious ones with desloppify exclude <path>.
Share any questionable candidates with me before excluding.

desloppify scan --path .
desloppify next

Notes:
--path is the directory to scan (use "." for the whole project, or "src/" etc).
use uv pip when pip command is not available
use uv to install python when python version is not met

Your goal is to get the strict score as high as possible. The scoring resists gaming — the
only way to improve it is to actually make the code better.

THE LOOP: run next. It tells you what to fix, which file, and the resolve command to run
when done. Fix it, resolve it, run next again. Over and over. This is your main job.

Don't be lazy. Large refactors and small detailed fixes — do both with equal energy. No task
is too big or too small. Fix things properly, not minimally.

Use plan to reorder priorities or cluster related issues. Rescan periodically. The scan
output includes agent instructions — follow them, don't substitute your own analysis.

使用中文总结

$ARGUMENTS
