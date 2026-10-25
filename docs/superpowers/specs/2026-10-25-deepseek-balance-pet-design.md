# DeepSeek 余额桌宠 — 设计文档

- 日期：2026-10-25
- 项目名：DeepSeek Balance Pet（DeepSeek 余额桌宠）
- 状态：已按用户反馈修订，等待实现
- 本地开发目录：`D:\Projects\deepseek-balance-pet`
- 修订 2026-10-25（试用反馈）：气泡改为**点击后约 0.75 秒分三段形成**（下面的小圈 → 中圈 → 大气泡，文字最后浮现），再点只刷新不收起，默认 10 秒自动淡出；恢复原版手绘气泡皮肤（角色/气泡分层）；窗口右上角使用**齿轮设置按钮**，点开是**原版风格的单列紧凑设置浮层**（改动立即生效，账户设置走「管理…」子窗口）；峰谷状态改为**方块徽章**（低谷=绿色方块白字「谷」，高峰=红色方块白字「峰」）并与大概时间一起居中，支持默认 / 梁文峰谷 / !?强强?! / 简洁（谷/峰，默认）四种文案；新增原版「小黄鸭」点击音效（SDL 8 通道混音，跟随系统输出）；字体略微加大；设置里拖动大小/透明度实时预览并立即保存；角色按屏幕左右自动翻转朝向；数字与呼吸动画更平滑、字体抗锯齿。

## 0. 最重要的声明：不需要 DSH

**本项目是一个完全独立的 Windows 桌面程序，不需要 DSH（DeepSeek Harness），不安装、不读取、不调用 `.dsh` 目录或 `dsh plugin`。**

- 只依赖：Windows + 一个 DeepSeek API Key（`sk-...`）。
- DSH 插件的 README 只作为小鲸鱼角色素材（MIT）的来源与灵感致谢，不是运行依赖。
- 复用 Claude Code 里已有的 DeepSeek Key 只是可选的便利功能；没有 Claude Code 也能正常使用。
- 上述声明必须出现在：README 第一屏、首次启动向导第一屏、关于窗口、Release 说明、GitHub 仓库描述。

## 1. 目标与非目标

### 目标

1. 在 Windows 10/11 桌面常驻一只小鲸鱼娘，气泡中实时显示 DeepSeek 剩余余额。
2. 60 秒自动刷新；点击鲸鱼立即刷新；断网时保留上次金额。
3. 前端可更换 / 测试 API Key；Key 加密存储，不出现明文。
4. 面向普通用户发布：免安装 exe（PyInstaller），同时保留源码安装方式。
5. 面向 GitHub 开源：中英双语界面与 README、CI、Release 工作流、配置文档、隐私说明。

### 非目标（第一版不做）

- macOS / Linux。
- 自动下载更新（只提供「检查更新」跳转）。
- 安装包 / 代码签名。
- 详细消费统计、多厂商余额。
- 多 Key 管理、自定义角色包、音效。
- 任何 DSH 集成。

## 2. 用户体验

### 首次启动

1. 检测系统语言（中文 / 其他）。
2. 检测可用 Key 来源：
   - 已配置的自定义 Key（DPAPI）
   - 环境变量 `DEEPSEEK_API_KEY`
   - Claude Code 用户配置 `~/.claude/settings.json` 的 `env.ANTHROPIC_AUTH_TOKEN`
3. 向导第一屏上方固定显示：**「无需 DSH · 独立运行」**。
4. 用户选择：使用检测到的 Key / 自己粘贴 Key / 先跳过。
5. 「测试连接」成功后保存；失败显示脱敏原因，可重试或跳过。
6. 完成，鲸鱼出现在右下角。

### 日常使用

- 左键拖动；单击鲸鱼后气泡约 0.75 秒分三段形成（小圈 → 中圈 → 大气泡，文字最后）并立即刷新；有气泡时再点只刷新，不收起；刷新时轻微 Q 弹；金额变化时数字滚动。
- 气泡中间显示峰谷方块徽章与大概时间（不显示倒计时；北京时间；周末、调休周末、法定节假日按低谷）：低谷=绿色徽章白字，高峰=红色徽章白字；默认简洁文案「谷/峰」，也可切换「高峰期/低谷期」「梁文峰/梁文谷」「!?峰峰?!/!?谷谷?!」，长文案自动加宽徽章；右边紧跟 `12小时55分后`，精确到 5 分钟。
- 气泡底部显示 `今日已用 ¥x.xx`：按余额下降观测累计，充值/赠金不会冲掉已用；跨天（北京时间）自动重置；离线时追加「离线」。
- 气泡默认隐藏，默认 10 秒后自动淡出，可设置秒数（0 = 不自动）。
- 窗口右上角常驻齿轮按钮，气泡隐藏时也可见；点开是原版风格的单列紧凑设置浮层。
- 按下角色瞬间播放一次原版「小黄鸭」音效；使用 SDL 8 通道混音并跟随系统当前输出设备，连点每次都能出声，按住不持续响；设置浮层可关闭「点击音效」。
- 角色按屏幕位置自动转向屏幕中心：左半边朝右，右半边朝左。
- 右键菜单：立即刷新、设置…、大小（小/中/大）、显示气泡、开机自启、隐藏 1 小时、关于、退出。
- 托盘图标：左键显示/隐藏，双击打开设置，右键同菜单。
- 位置、大小、透明度、语言自动保存。

### 设置浮层（原版风格单列）

点右上角齿轮按钮，打开约 320px 宽的白色圆角浮层；没有页签和保存/取消，改动立即生效并写入配置。行顺序：

1. 大小（滑块 + 数字，实时预览）
2. 透明度（滑块 + 百分比，实时预览）
3. 启用气泡
4. 点击音效
5. 呼吸动画
6. 数字滚动动画
7. 减少动态效果
8. 气泡自动隐藏秒数（默认 10）
9. 峰谷文案（默认 / 梁文峰谷 / !?强强?! / 简洁）
10. 刷新间隔（30–600 秒）
11. 开机自启
12. 始终置顶
13. 语言（自动/中文/English，重启后生效）
14. 高级：超时 / 代理 / API 地址（「设置…」子窗口）
15. 账户与 API Key：显示当前来源与尾号；「管理…」打开子窗口，可粘贴/测试/清除 Key
16. 位置：重置
17. 底部小号版本号：点击打开「关于」（无需 DSH、版本、许可）

浮层是**非模态工具窗**：打开时鲸鱼仍可点击、拖动、刷新；点右上角 ×、再点齿轮或按 Esc 关闭。

## 3. 架构

```
src/deepseek_pet/
├─ __main__.py        # 入口：python -m deepseek_pet / deepseek-pet
├─ cli.py             # --check --fake-balance --portable --reset-config --version
├─ app.py             # QApplication、单实例、启动流程
├─ config.py          # 默认值、校验、迁移、原子写入、损坏恢复
├─ secrets_store.py   # Windows DPAPI 加解密（ctypes，无额外依赖）
├─ key_source.py      # 自定义 > 环境变量 > Claude Code 配置；尾号脱敏
├─ balance_client.py  # GET /user/balance、解析、错误分类、脱敏
├─ usage.py           # 今日已用：按余额下降观测累计、跨天重置
├─ i18n.py            # 中英文字典 + 系统语言检测
├─ logging_setup.py   # 轮转日志 + Key 脱敏过滤器
└─ ui/
   ├─ pet_window.py   # 透明置顶窗口、气泡绘制、拖拽、动画
   ├─ settings_dialog.py
   ├─ first_run.py
   ├─ tray.py
   └─ styles.py
```

- GUI：PySide6（Qt 6）。透明背景、无边框、置顶、不抢焦点。
- 网络：`requests`，在 `QThreadPool` 后台执行，通过信号回主线程；同一时间只允许一个在途请求。
- 单实例：`QLocalServer/QLocalSocket`，第二次启动唤醒已有实例。
- 资源：`assets/DSniang02.png`（角色 + 气泡）、`assets/DSniang1.png`（托盘）、`assets/icon.ico`（exe 图标，由 PNG 生成）。
- 打包：`packaging/deepseek-pet.spec` + `packaging/build.ps1`（PyInstaller onedir）。

## 4. 配置系统

- 位置：`%APPDATA%\DeepSeekPet\config.json`；程序目录存在 `portable.txt` 时使用 `<程序目录>\data\config.json`。
- 原子写入（临时文件 + 替换）；损坏时备份为 `config.json.bak` 并回默认值。
- 带 `schema_version`，提供迁移函数；设置窗口与 CLI 均可恢复默认。

```json
{
  "schema_version": 1,
  "language": "auto",
  "refresh_interval_sec": 60,
  "pet_size": 360,
  "opacity": 1.0,
  "always_on_top": true,
  "show_bubble": true,
  "position": {"x": null, "y": null},
  "startup": false,
  "key_source": "auto",
  "api": {"base_url": "https://api.deepseek.com", "timeout_sec": 10, "proxy": ""},
  "ui": {"number_animation": true, "reduce_motion": false},
  "update_check": true,
  "first_run_done": false,
  "last_balance": null
}
```

校验规则：数值越界自动夹到范围内；未知字段保留；语言只允许 `auto/zh/en`。

## 5. Key 管理

- 来源优先级：**自定义 Key（DPAPI） > `DEEPSEEK_API_KEY` > `~/.claude/settings.json` 的 `env.ANTHROPIC_AUTH_TOKEN`**。
- 自定义 Key 使用 Windows DPAPI（`CryptProtectData` / `CryptUnprotectData`，`CRYPTPROTECT_UI_FORBIDDEN`）加密后存 `secrets.bin`；绑定当前 Windows 用户，换机无法解密。
- 界面只显示尾 4 位，例如 `sk-••••1a2b`。
- 日志、异常、诊断导出统一用正则脱敏 `sk-[A-Za-z0-9_-]{8,}`。
- 设置窗口提供「测试连接」：直接请求 `/user/balance`，成功显示余额，失败显示脱敏的 HTTP/网络错误。

## 6. 网络与错误处理

- 请求：`GET https://api.deepseek.com/user/balance`，`Authorization: Bearer <key>`，默认超时 10 秒。
- 解析：优先 `currency == "CNY"` 的 `balance_infos`，否则取第一条；显示 `total_balance`，两位小数。
- 错误分类与提示：
  - 未找到 Key →「未找到 DeepSeek API Key，请在设置中填写」
  - 401/403 →「Key 无效或无余额权限」
  - 429 →「请求过于频繁，稍后重试」
  - 超时/断网 →「离线 · 显示上次余额（HH:MM）」
  - 其他 →「服务异常（HTTP xxx）」
- 任一错误都保留上次成功余额；连续失败自动退避（60 → 120 → 300 秒），手动点击立即重置。
- 启动后立即刷新一次；成功余额写入配置的 `last_balance`，离线重启也能显示。

## 7. 界面细节

- 窗口为 `DSniang02.png` 整图，默认 360×360，按设备像素比渲染，缩放清晰。
- 气泡内三行：标题小字「DeepSeek 余额」、金额大字（带货币符号）、状态小字。
- 透明区域按 alpha mask 设置窗口区域，尽量减少误点；拖动阈值 4px，区分点击与拖动。
- 数字滚动约 500ms；`reduce_motion` 或系统「减少动画」开启时直接切换。
- 位置保存做 500ms 防抖；启动时若窗口完全在屏幕外，回到主屏右下角。
- 中英文文案集中在 `i18n.py`，测试保证 key 对齐。

## 8. 打包与分发（本地优先）

### 第一阶段：本地试用版（本次要做）

- 在本地构建并运行，**不推送 GitHub、不创建 Release**。
- 提供源码运行方式与本地 PyInstaller 免安装包，供用户先测试。
- 版本号 `0.1.0`，`CHANGELOG.md` 记录。

### 第二阶段：用户测试通过后再发布（本次不做）

- 仓库预置 `.github/workflows/release.yml`：推 `v*` tag 时 Windows 构建、生成 `SHA256SUMS.txt`、创建 Release。
- 产物：`DeepSeekPet-0.1.0-win-x64.zip`（onedir，含 exe、assets、LICENSE、README）。
- 未签名，README 说明 SmartScreen 提示处理方式。
- GitHub 仓库名 `deepseek-balance-pet`，描述第一句写明「无需 DSH」。

## 9. 测试

- 单元测试：
  - 余额 JSON：CNY、USD、多币种、空列表、字段缺失、畸形 JSON。
  - 配置：默认值、范围夹取、损坏恢复、迁移、原子写入。
  - Key 来源优先级、尾号脱敏、日志脱敏。
  - i18n 中英文 key 对齐。
  - DPAPI 往返（非 Windows 自动跳过）。
- GUI 冒烟：`QT_QPA_PLATFORM=offscreen` + `--fake-balance`。
- 手动验收：
  - 首次向导三种 Key 来源。
  - 点击刷新、数字动画、断网保留旧值。
  - 拖拽后重启恢复位置。
  - 托盘退出、开机自启开关。
  - 无 DSH 环境下完整可用（本机即无 DSH，天然验证）。

## 10. 安全与隐私

- 仅访问 `api.deepseek.com`；`update_check` 开启时访问 `api.github.com`。
- 无遥测、无账号系统、不上传任何使用数据。
- Key 只存 DPAPI 密文或原配置位置；日志与诊断导出全部脱敏。
- 设置与配置只写本机。
- `SECURITY.md` 说明存储方式与漏洞报告渠道。

## 11. 许可与署名

- 本项目代码：MIT。
- 角色素材来自 `MeteorNOX/DeepSeek-Balance-Whale-Widget`（MIT）；在 `THIRD_PARTY_NOTICES.md` 保留原作者署名与 MIT 全文。
- README 注明：非官方项目，与 DeepSeek 官方无关；不需要 DSH。

## 12. 验收标准

1. 在一台没有 DSH 的 Windows 机器上，解压/启动后能看到鲸鱼与余额，无需 DSH、无需 Claude Code。
2. 设置窗口可更换 Key、测试连接、清除 Key。
3. 60 秒自动刷新；点击立即刷新；断网保留旧值。
4. 配置、位置、大小、语言在重启后保持。
5. `pytest` 与 `ruff` 全绿；本地 exe 可启动并正常显示。
6. README 第一屏明确写有「无需 DSH / No DSH required」。
