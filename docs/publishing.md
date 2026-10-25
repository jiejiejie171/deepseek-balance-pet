# 发布到 GitHub（维护者清单）

> **当前状态：尚未推送、尚未创建 GitHub Release。** 等你确认后再执行本页命令。

## 1. 发布前检查

- [ ] 版本号：`pyproject.toml`、`src/deepseek_pet/__init__.py`、`CHANGELOG.md`、
      `README.md` / `README.en.md` 中的版本一致（当前 `0.2.0`）。
- [ ] `python -m pytest -q` 全绿，`python -m ruff check src tests` 通过。
- [ ] `dist/DeepSeekPet/DeepSeekPet.exe --self-test` 退出码 0。
- [ ] 新 exe 能正常显示桌宠、气泡、设置浮层、音效。
- [ ] `dist/DeepSeekPet-0.2.0-win-x64.zip` 内含 exe、`_internal/`、README、LICENSE、
      THIRD_PARTY_NOTICES，且 `_internal/pygame/SDL2.dll` 存在。
- [ ] 对真实 API Key 做一次精确扫描：仓库、`dist/`、zip 均无命中。
- [ ] `git status` 干净；没有 `secrets.bin`、`config.json`、`data/` 或 `.claude/` 被跟踪。
- [ ] README 顶部有免责声明与原作者署名；`DISCLAIMER.md`、`THIRD_PARTY_NOTICES.md` 已链接。
- [ ] `git log` 里的作者身份是正确的（本地开发提交目前使用占位身份
      `DeepSeek Pet Dev <dev@localhost>`，发布前请改成你自己的 GitHub 用户名/邮箱）。

## 2. 仓库信息建议

- 仓库名：`deepseek-balance-pet`
- 描述：`无需 DSH 的独立 Windows 桌面小鲸鱼：实时显示 DeepSeek 余额、峰谷、今日已用。`
- Topics：`deepseek` `desktop-pet` `pyside6` `windows` `balance-widget`
- 首页：`README.md`；英文：`README.en.md`
- 不建议勾选自动生成 README/LICENSE，仓库里已有。

## 3. 本地准备（等你确认后执行）

```powershell
cd D:\Projects\deepseek-balance-pet

# 改成你自己的 GitHub 身份（示例）
git config user.name "你的名字"
git config user.email "你的邮箱"

# 把默认分支改为 main（如果你希望用 main）
git branch -M main

# 添加远程仓库（先由你在 GitHub 创建空仓库）
git remote add origin https://github.com/<你的用户名>/deepseek-balance-pet.git
git push -u origin main
```

## 4. 创建 Release

> **v0.2.0 已手动发布**：`release.yml` 已恢复；之后推送 `v*` tag 会自动构建并创建 Release。

1. 打 tag 并推送：

   ```powershell
   git tag v0.2.0
   git push origin v0.2.0
   ```

2. 在 GitHub 创建 Release：
   - Tag：`v0.2.0`
   - 标题：`v0.2.0 — 无需 DSH 的独立桌宠`
   - 附件：`dist/DeepSeekPet-0.2.0-win-x64.zip`
   - 如启用 `.github/workflows/release.yml`，推 tag 后会自动构建并上传；也可以按本页手动上传现有 zip。

3. Release 说明必须包含：
   - **无需 DSH / No DSH required**；
   - 非官方、与 DeepSeek/原作者无隶属关系的免责声明；
   - 原作者 MeteorNOX 与素材 MIT 许可；
   - 版本、系统要求、API Key 配置入口；
   - 如提供 SHA256，附上校验值。

4. 生成 SHA256（可选但推荐）：

   ```powershell
   Get-FileHash dist\DeepSeekPet-0.2.0-win-x64.zip -Algorithm SHA256
   ```

## 5. 发布后检查

- [ ] 仓库首页第一屏能看到「无需 DSH」、免责声明、原作者署名。
- [ ] Release 的 zip 可下载，解压后 exe 能启动。
- [ ] 新用户的首次启动向导能填写 Key 并测试连接。
- [ ] 没有把 `%APPDATA%\DeepSeekPet`、`~/.claude`、日志或密钥提交到仓库。
- [ ] 如果之后修改了 README/素材，重新构建 zip 并更新 Release，避免包内文档过期。

## 6. 不要做的事

- 不要在仓库、Issue、Release 或截图中粘贴真实 API Key。
- 不要提交 `%APPDATA%\DeepSeekPet\secrets.bin`、`config.json` 或 `~/.claude/settings.json`。
- 不要在未确认的情况下推送或创建公开 Release。
