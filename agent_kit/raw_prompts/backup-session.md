---
description: backup codex session
---
请扫描本地 Codex session 历史文件，做一次私有备份上传，并严格按以下要求执行：

1. 扫描本地 Codex 历史文件，重点包括：
- `~/.codex/history.jsonl`
- `~/.codex/sessions/`

2. 将这些文件打包压缩成一个归档文件。

3. 归档完成后，用 `openssl` 做对称加密。
参考命令: openssl enc -aes-256-cbc -pbkdf2 -salt -iter 200000
当前密码先配置为：
- `123456`

4. 检查是否存在仓库, 没有的话使用 `gh` 创建一个新的 GitHub 私有仓库，仓库名设为：
- `codex-backup`

5. 只上传加密后的文件，不要上传明文归档。
使用 Git LFS。

6. README 需要补一份简洁说明和时间线，至少包含：
- 备份来源
- 归档内容
- session 文件数量
- 起止日期
- 大小信息
- SHA-256
- 按月统计的 session 数量
- 加密和解密命令参考
- GitHub 上通过 Git LFS 存储

7. README 中不要出现具体用户目录。
所有原本类似 `/Users/<name>/...` 的路径统一写成：
- `~/.codex/...`

8. README 可以写解密命令示例，但不要把密码写进 README。

9. 上传完成后，确认：
- 远端私有仓库存在
- 默认分支正常
- 当前分支只保留 `README.md`、`.gitattributes` 和加密后的备份文件
- 不要保留明文归档在当前分支里

10. 清理本地 `/tmp` 或 `/private/tmp` 下本次生成的临时归档、临时仓库和所有明文文件。

11. 最后汇报：
- 私有仓库地址
- 加密后的备份文件名
- 使用的 openssl 加密命令或算法
- SHA-256
- 本地临时文件是否已清理
