# 免责声明 / Disclaimer

## 中文

### 非官方项目

本项目（DeepSeek 余额桌宠 / DeepSeek Balance Pet）是个人开发的开源项目，**不是** DeepSeek 官方产品，**不是** DeepSeek Harness（DSH）插件，也与 DeepSeek 官方、DSH 项目及原作者 **MeteorNOX** 不存在任何隶属、合作、赞助或背书关系。

### 素材与原作者

- 小鲸鱼角色图片、点击音效等素材来自 **MeteorNOX** 的
  [DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget)，
  按 MIT 许可使用。
- 本项目仅把这些素材用于一个独立的 Windows 桌面程序，不代表原作者的观点或维护承诺。
- 完整许可与署名见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

### 数据准确性

- 余额、峰谷状态和“今日已用”来自本机对 `https://api.deepseek.com/user/balance` 的请求与观测。
- “今日已用”是按余额下降累计的**本地估算**，不是官方账单；充值、赠金、退款、余额调整、并发使用、接口延迟等都可能造成差异。
- 峰谷规则按北京时间本地计算，可能随 DeepSeek 官方政策调整而变化；本项目不保证规则始终最新。
- 请以 DeepSeek 官方账单和账户页面为准，**不要将本软件用于对账、报销、审计或法律用途**。

### API Key 与账户安全

- 你的 API Key 由你自行创建、保管和撤销。
- 自定义 Key 使用 Windows DPAPI 加密保存在本机；程序不会主动上传 Key，但会按功能需要把 Key 发给 `api.deepseek.com`（或你在“高级”里自行配置的 API 地址）。
- 请自行确认代理、网络环境和自定义 API 地址可信；不要把 Key 写入公开仓库、截图或日志。
- 因 Key 泄露、账户被滥用或产生费用造成的损失，由使用者自行承担。

### 无担保与责任限制

- 本软件按 MIT 许可“AS IS”提供，不提供任何明示或暗示的担保，包括但不限于适销性、特定用途适用性和不侵权担保。
- 在法律允许的最大范围内，作者与贡献者不对因使用或无法使用本软件产生的任何直接、间接、偶然、特殊或后果性损失承担责任。
- 你可以自行修改和分发代码，但需遵守 [LICENSE](LICENSE) 与第三方许可。

### 商标

DeepSeek、DeepSeek Harness 及相关名称、标识归其权利人所有。本项目仅作描述性使用，不表示任何官方关联。

---

## English

### Unofficial project

DeepSeek Balance Pet is an independent open-source project. It is **not** an official DeepSeek product, **not** a DeepSeek Harness (DSH) plugin, and has no affiliation, partnership, sponsorship, or endorsement relationship with DeepSeek, the DSH project, or the original artist **MeteorNOX**.

### Artwork and original author

- The whale-girl artwork and click sound come from **MeteorNOX**'s
  [DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget),
  used under the MIT license.
- This project uses those assets in a standalone Windows application and does not represent
  the original author's views or maintenance commitments.
- See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the full notices.

### Data accuracy

- Balance, peak/off-peak status, and "used today" are based on local requests to
  `https://api.deepseek.com/user/balance` and local observation.
- "Used today" is a **local estimate** accumulated from balance decreases, not an official
  bill. Top-ups, granted credit, refunds, balance adjustments, concurrent usage, and API
  latency can cause differences.
- Peak/off-peak rules are computed locally in Beijing time and may change when DeepSeek
  updates its policy; this project does not guarantee they are always current.
- Always refer to DeepSeek's official bill and account page. **Do not use this software for
  reconciliation, reimbursement, auditing, or legal purposes.**

### API key and account security

- You create, store, and revoke your own API key.
- A custom key is encrypted locally with Windows DPAPI; the app does not intentionally upload
  it, but it sends the key to `api.deepseek.com` (or an API base URL you configure under
  Advanced) as needed for the balance feature.
- Verify that your proxy, network, and custom API endpoint are trustworthy. Never commit a
  key, paste it into a screenshot, or write it to a public log.
- You are responsible for any loss caused by key leakage, account abuse, or charges.

### No warranty and limitation of liability

- The software is provided "AS IS" under the MIT license, without warranty of any kind,
  express or implied, including merchantability, fitness for a particular purpose, and
  non-infringement.
- To the maximum extent permitted by law, the authors and contributors are not liable for any
  direct, indirect, incidental, special, or consequential loss arising from the use of or
  inability to use this software.
- You may modify and redistribute the code under [LICENSE](LICENSE) and the third-party
  licenses.

### Trademarks

DeepSeek, DeepSeek Harness, and related names and marks belong to their respective owners.
This project uses them only descriptively and claims no official association.
