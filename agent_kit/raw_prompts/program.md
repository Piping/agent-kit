---
description: program with autoresearch 
---
目标
* 让 AI 代理自动做训练实验，持续优化 val_bpb（越低越好）。
启动前Setup
1. 先定 run tag（如 mar5），新建分支 autoresearch/<tag>
2. 阅读 3 个文件：README.md、prepare.py、train.py
3. 检查 ~/.cache/autoresearch/ 数据和 tokenizer 是否存在；没有就先跑 uv run prepare.py
4. 新建 results.tsv（只写表头）
5. 确认后开始实验循环
实验规则
* 每次训练固定 5 分钟：uv run train.py
* 只能改 train.py
* 不能改 prepare.py
* 不能加新依赖
* 评估指标以 prepare.py 里的 evaluate_bpb 为准
结果记录（results.tsv）
* 列：commit, val_bpb, memory_gb, status, description
* status 取值：keep / discard / crash
* crash 时 val_bpb=0.000000, memory_gb=0.0
循环流程（核心）
1. 基于当前提交改 train.py（一个实验点）
2. git commit
3. 跑训练并重定向日志：uv run train.py > run.log 2>&1
4. 提取结果：grep val_bpb 和 peak_vram_mb
5. 写入 results.tsv（不要提交这个文件）
6. 若 val_bpb 变好：保留提交（advance）
7. 若不变或变差：回滚到实验前提交
异常处理
* 10 分钟还没结束：判失败，终止并回滚
* 崩溃：能快速修就修后重跑；否则记 crash，继续下一个点
原则
* 优先简单有效；为很小收益引入复杂代码不值。
* 基线实验必须先跑一次原始 train.py。
* 进入循环后默认持续运行，直到人工叫停。
* 分析问题时总是使用 STAR 思考模式
额外要求
$ARGUMENTS
