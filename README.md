# OSINT Recon Dual Mode

一个更“硬核”的 OSINT / 信息收集项目，支持：

- **CMD 模式**：适合自动化、批处理、脚本化
- **GUI 模式**：适合手工调研、快速查看结果

> 仅用于合法授权的安全评估、资产盘点与公开信息调研。

## 功能

- 目标标准化（URL / 域名 / IP）
- DNS 解析（A 记录）
- HTTP 标头抓取
- robots.txt / sitemap.xml 检查
- 首页邮箱提取（正则）
- 结果导出为 JSON

## 目录结构

- `osint_core.py`：核心采集逻辑
- `osint_cli.py`：命令行入口
- `osint_gui.py`：图形界面入口（Tkinter）
- `requirements.txt`：可选依赖

## 安装

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

> 不装依赖也可以运行（会走标准库降级路径）。

## CMD 模式

```bash
python osint_cli.py --target example.com --out result.json
```

可选参数：

- `--timeout 12`
- `--user-agent "Mozilla/5.0 ..."`

## GUI 模式

```bash
python osint_gui.py
```

输入目标后点击“开始收集”，可一键保存 JSON。

## 结果示例字段

- `target_input`
- `normalized`
- `dns`
- `http_headers`
- `robots`
- `sitemap`
- `emails`
- `timestamp`

## 路线图

- [ ] 子域名爆破（被动源整合）
- [ ] 证书透明日志（CT）聚合
- [ ] 截图采集（首页快照）
- [ ] 插件化数据源

## License

MIT
