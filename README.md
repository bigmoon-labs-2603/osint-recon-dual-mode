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
- 结果导出为 JSON

## 目录结构

- `osint_core.py`：核心采集逻辑
- `osint_cli.py`：命令行入口
- `osint_gui.py`：图形界面入口（Tkinter）
- `requirements.txt`：可选依赖
- `.gitignore`：忽略缓存与临时文件

## 安装

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

> 不装依赖也可以运行（会走标准库降级路径），但推荐安装 `requests`。

## CMD 模式

```bash
python osint_cli.py --target example.com --out result.json
```

可选参数：

- `--timeout 12`
- `--user-agent "Mozilla/5.0 ..."`
- `--no-verify-tls`（实验环境可用，不建议生产）
- `--no-subdomains`（关闭被动子域名收集）

## GUI 模式

```bash
python osint_gui.py
```

GUI 支持：

- 目标输入
- 勾选 TLS 验证
- 勾选被动子域名收集
- 一键保存 JSON

## 结果示例字段

- `target_input`
- `normalized`
- `dns`
- `http_headers`
- `web.title`
- `web.emails`
- `robots`
- `sitemap`
- `security_txt`
- `subdomains`
- `errors`
- `timestamp`

## 安全与合规

- 本项目不包含漏洞利用、爆破、提权等攻击能力
- 仅面向公开信息与被动调研
- 使用者需对目标授权与当地法律合规负责

## 路线图

- [ ] 插件化数据源（Shodan/Censys/FOFA 适配层）
- [ ] 截图采集（首页快照）
- [ ] 批量目标与并发任务队列
- [ ] Markdown / DOCX 报告导出

## License

MIT
