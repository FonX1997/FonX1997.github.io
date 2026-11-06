# Feng Li · Academic Homepage

李峰的中英双语学术主页，供 GitHub Pages 发布。

## 通过对话更新网站

本目录已连接 `FonX1997/FonX1997.github.io` 的 `main` 分支。完成一次仓库 Deploy key 写入授权后，可以直接在 Codex 中描述修改需求，由助手修改、检查并推送，GitHub Pages 自动重新发布。具体维护步骤见 `AGENTS.md`。

例如：“把这篇新论文加入论文列表，并更新线上主页”“首页优先展示平行控制研究”“更新中英文简介，并发布”。如需先看效果，可以明确说“先给我预览”。

## 发布到 GitHub Pages

1. 登录账号 **FonX1997**，创建公开仓库 **FonX1997.github.io**。
2. 将本目录中的文件和文件夹上传到仓库根目录。根目录应直接看到 `index.html`，同时保留 `assets` 目录及其中的文件。
3. 在仓库 **Settings → Pages** 中，选择 **Deploy from a branch**，分支选择 **main**，目录选择 **/ (root)**，点击 **Save**。
4. 等待 GitHub 完成发布后访问 **https://fonx1997.github.io/**。

## 页面与内容

- `index.html`：个人简介、近期动态、代表作、教育经历、学术服务。
- `research.html`：研究方向与科研项目。
- `publications.html`：14 篇第一／通讯作者论文，支持检索、年份筛选、BibTeX 复制与下载。
- 网站不提供个人简历 PDF 下载；原始中英文简历保留在本地，作为资料参考。
- `data/publications.json`：论文信息，期刊指标与接收状态按当前中文版简历填写；公开 DOI 的作者及卷页元数据已通过 Crossref 核对，SCIS 按期刊官网记录。
- `tools/build_site.py`：使用 Python 标准库重新生成全部页面与 BibTeX 文件。

无需安装依赖或运行框架。直接访问已生成的 HTML 即可；BibTeX 复制功能在 localhost 或 HTTPS 下可用。

更新数据后，在本目录运行 `python3 tools/build_site.py` 并重新上传生成的页面、`assets/publications.js` 和 BibTeX 文件。头像为 `assets/portrait.jpg`。

目前 QST、IJSS 两篇论文按简历标为已接收，未补造 DOI；ASC 使用 2027 年卷期年份。页面不含占位链接或虚构学术信息。
