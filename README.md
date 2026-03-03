# OSINT Recon Dual Mode

一个更“硬核”的 OSINT / 信息收集项目，支持：

- **CMD 模式**：适合自动化、批处理、脚本化
- **GUI 模式**：适合手工调研、快速查看结果

> 仅用于合法授权的安全评估、资产盘点与公开信息调研。

## 功能亮点

- 目标标准化（URL / 域名 / IP）
- DNS 解析（A 记录）
- HTTP 标头抓取（状态码、重定向后 URL、响应头）
- `robots.txt` / `sitemap.xml` / `.well-known/security.txt` 检查
- 首页 `title` 与邮箱提取（正则）
- 被动子域名收集（crt.sh）
- 批量目标并发收集（TXT）
- 报告导出（JSON / Markdown / DOCX）
- **插件化情报引擎接口：FOFA / Shodan / Censys**
- **风险评分引擎（0-100 + 风险分级 + 因子）**
- **情报时间线输出（报告内自动生成）**

## 目录结构

- `osint_core.py`：核心采集逻辑
- `plugins.py`：FOFA/Shodan/Censys 插件适配
- `risk_scoring.py`：风险评分引擎
- `batch_utils.py`：批量并发执行
- `report_export.py`：Markdown / DOCX 导出（含时间线）
- `osint_cli.py`：命令行入口
- `osint_gui.py`：图形界面入口（Tkinter）
- `targets-example.txt`：批量样例

## 环境变量（插件引擎）

按需配置，不配置也能运行基础能力：

- FOFA: `FOFA_EMAIL`, `FOFA_KEY`
- Shodan: `SHODAN_API_KEY`
- Censys: `CENSYS_API_ID`, `CENSYS_API_SECRET`

## CMD 模式

### 单目标

```bash
python osint_cli.py --target example.com --plugins fofa,shodan,censys --out result.json --export-md report.md --export-docx report.docx
```

### 批量目标

```bash
python osint_cli.py --targets-file targets-example.txt --workers 8 --plugins fofa,shodan --out batch.json --export-md batch.md --export-docx batch.docx
```

可选参数：

- `--timeout 12`
- `--user-agent "Mozilla/5.0 ..."`
- `--no-verify-tls`
- `--no-subdomains`
- `--plugins fofa,shodan,censys`
- `--no-risk`

## GUI 模式

```bash
python osint_gui.py
```

GUI 支持：

- 单目标 / 批量文件 两种输入
- Worker 并发配置
- TLS 校验开关
- 被动子域名开关
- 风险评分开关
- 插件列表输入（逗号分隔）
- 一键导出 JSON / MD / DOCX

## 安全与合规

- 本项目不包含漏洞利用、爆破、提权等攻击能力
- 仅面向公开信息与被动调研
- 使用者需对目标授权与当地法律合规负责

## License

MIT
