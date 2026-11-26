# NCS Paper Figure Gallery

> **全学科 Nature / Science / Cell 正刊及子刊论文主图灵感画廊（2024–2026 Open Access · 3,000+ 主图）**

在线浏览网站：**https://daydayup-xq.github.io/ncs-paper-figure-gallery/**  
GitHub 仓库：**https://github.com/daydayup-xq/ncs-paper-figure-gallery**

一个可直接部署到 **GitHub Pages** 的纯静态学术配图灵感网站：收录 **Nature、Science、Cell 三大正刊及其核心大子刊、综合/小子刊** 最近三年（**2024–2026**）的 **Open Access** 论文主图（`Figure 1` 与 `Graphical Abstract`），按**学科方向**、**出版体系**、**期刊级别**与**主图视觉类型**多维筛选，并自动提取每张顶刊主图的实测配色色板（支持一键复制 HEX / Python / R / CSS 与 BibTeX）。

## 核心特性

- **100% Open Access 合规数据源**：
  - 论文元数据通过 **OpenAlex Works API** 检索最近三年（2024–2026）OA 论文。
  - 原图直接引用 **Springer Nature 官方 CDN** (`media.springernature.com`)、**Elsevier 官方 CDN** (`ars.els-cdn.com`) 与 **NCBI PMC Open Access 官方 S3 数据集** (`pmc-oa-opendata.s3.amazonaws.com`)，零盗图、保留完整 DOI / PMCID / 作者 / 开源许可署名。
- **全学科 6 大方向划分**：
  - 🧬 生命科学与医学 (`bio-med`)
  - 🧪 材料与化学纳米 (`mat-chem`)
  - ⚡ 能源、地球与环境 (`energy-env`)
  - ⚛️ 物理、光学与工程 (`phys-eng`)
  - 🤖 AI 与计算科学 (`ai-comp`)
  - 🌐 交叉学科与行为社会 (`inter-soc`)
- **NCS 专属期刊矩阵（正刊 → 核心大子刊 → 综合/小子刊）**：
  - ★ 三大正刊 (`Flagship`)：*Nature*, *Science*, *Cell*
  - 核心大子刊 (`Major Sub-journals`)：*Nature Materials*, *Nature Energy*, *Nature Machine Intelligence*, *Nature Medicine*, *Nature Microbiology*, *Nature Immunology*, *Science Translational Medicine*, *Science Immunology*, *Science Robotics*, *Joule*, *Chem*, *Matter*, *Cancer Cell*, *Developmental Cell*, *Current Biology*, *Immunity*, *Neuron* 等 60+ 本专刊大子刊
  - 综合/小子刊 (`Minor / OA Sub-journals`)：*Nature Communications*, *Science Advances*, *Cell Reports*, *iScience*
- **顶刊色板提取与实验室工具箱**：
  - 每张卡片底部展示从原图像素量化提取的 5 色主色板，点击色块即刻复制 HEX；
  - Lightbox 大图检视支持 1:1 缩放、键盘 `←` / `→` 翻页、Python (`matplotlib`) / R (`ggplot2`) / CSS 色板代码导出、BibTeX 复制及 DOI / PMC 直达。
- **URL 参数联动**：支持分享带筛选状态的链接，例如 `?y=2026`、`?tier=flagship`、`?family=nature&discipline=mat-chem&y=2025`。

## 本地运行与更新数据

```bash
# 1. 本地预览网站（任意静态服务器即可，或直接双击 index.html）
python -m http.server 8080

# 2. 增量抓取并扩展最近三年（2024-2026）OA 论文主图至 3,000+ 张
python -X utf8 scripts/crawl_ncs_figures.py --merge --target-total 3200 --workers 32

# 3. 校验数据集完整性与前端静态资源
python -X utf8 scripts/validate_gallery.py
```

## GitHub Pages 自动部署

- 仓库地址：`https://github.com/daydayup-xq/ncs-paper-figure-gallery`
- 在线访问：`https://daydayup-xq.github.io/ncs-paper-figure-gallery/`
- 内置工作流：
  - `.github/workflows/deploy-pages.yml`：每次推送到 `main` 分支自动发布静态站点。
  - `.github/workflows/update-figures.yml`：每月 1 日 03:00 UTC（北京时间 11:00，`0 3 1 * *`）自动抓取最新近三年 OA 主图、提交仓库并自动重新部署 GitHub Pages（也支持在 GitHub Actions 页面手动触发）。
