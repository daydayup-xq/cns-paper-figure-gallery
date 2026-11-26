<div align="center">

<p align="center">🌐 <strong>简体中文</strong> · <a href="README.en.md">English</a></p>

<img src="docs/banner.png" alt="NSC 顶刊论文主图灵感画廊横幅" width="920">

# 🎨 NSC 顶刊论文主图灵感画廊
### Nature · Science · Cell 正刊与子刊论文主图灵感画廊 · 全学科 · 2024–2026

### 💖 寻求赞助与资源支持

**让科研绘图灵感持续开放，让全学科配色与版式参考触手可及。**

欢迎个人与机构提供 **资金赞赏、AI 模型 / API 额度或云算力支持**，用于支持图库持续扩展、每月自动采集维护与配色工具迭代。也欢迎通过点 Star、推荐期刊或分享给课题组同伴支持本项目！

**♡ 个人赞赏支持：[跳转赞赏码](#-支持作者) · 在线支持页：[support.html](https://daydayup-xq.github.io/ncs-paper-figure-gallery/support.html)**

[![Website](https://img.shields.io/website?down_color=lightgrey&label=Gallery&up_color=blue&up_message=online&url=https://daydayup-xq.github.io/ncs-paper-figure-gallery/)](https://daydayup-xq.github.io/ncs-paper-figure-gallery/)
![Figures](https://img.shields.io/badge/figures-5%2C270-orange)
![Flagship·Subjournal·OA](https://img.shields.io/badge/Flagship%C2%B7Sub%C2%B7OA-2134%C2%B72484%C2%B7652-gold)
![Journals](https://img.shields.io/badge/journals-Nature%C2%B7Science%C2%B7Cell%20(68)-purple)
![Years](https://img.shields.io/badge/years-2024--2026-success)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](scripts/crawl_ncs_figures.py)
[![License: MIT](https://img.shields.io/badge/code%20license-MIT-green.svg)](LICENSE)
[![Images license](https://img.shields.io/badge/images-CC%20BY%20%2F%20PMC%20OA-yellow.svg)](#-%E7%89%88%E6%9D%83)
![Last commit](https://img.shields.io/github/last-commit/daydayup-xq/ncs-paper-figure-gallery)
![Stars](https://img.shields.io/github/stars/daydayup-xq/ncs-paper-figure-gallery?style=social)

<p align="center">🌐 <strong>简体中文</strong> · <a href="README.en.md">English</a></p>

画论文主图前，先看 Nature、Science、Cell 怎么排版与配色。  
一个可搜索、可多维筛选、可一键提取实测色卡的 Figure 1 / Graphical Abstract 画廊。纯静态、零构建、可离线打开。

[🌐 在线画廊](https://daydayup-xq.github.io/ncs-paper-figure-gallery/) ·
[🎨 实测色卡提取](#-实测色卡提取) ·
[📊 收录规模](#-收录规模) ·
[🧭 视觉模式](#-视觉模式) ·
[🚀 快速开始](#-快速开始) ·
[♡ 支持作者](#-支持作者)

</div>

## 🤝 赞助伙伴

感谢以下赞助伙伴为本项目生态与科研效率工具提供支持。点击横幅或链接即可访问，完整说明可展开查看。

<table>
  <tr>
    <td width="50%" valign="top">
      <a href="https://xqai.top"><strong>XQAI · AI 会员自助充值中心</strong></a><br>
      <a href="https://xqai.top"><img src="docs/xqai-banner.svg" alt="XQAI AI 会员自助充值中心 — ChatGPT Plus / Pro" width="430"></a><br>
      <sub>ChatGPT Plus / Pro 24 小时自助充值 · 无需密码｜<a href="https://xqai.top"><strong>访问 xqai.top ↗</strong></a></sub>
      <details>
        <summary><sub>详细介绍与使用说明</sub></summary>
        <p>感谢 <strong>XQAI (https://xqai.top)</strong> 对本项目的赞助支持！</p>
        <ul>
          <li><strong>安全自助充值，告别代充风险</strong>：全程官方卡密自助操作，<b>无需向第三方提供账号密码</b>，避免手工代充导致的封号与隐私风险。</li>
          <li><strong>24 小时全自动开通/续费</strong>：支持 ChatGPT Plus 与 ChatGPT Pro 会员自助充值，论文投稿冲刺与日常科研随时可用。</li>
          <li><strong>科研绘图高效搭档</strong>：在本画廊筛选出目标顶刊的 <code>Figure 1</code> 构图与 <code>Python / R</code> 实测 HEX 色卡后，可直接交由 ChatGPT Plus / Pro 生成高质量 <code>matplotlib</code> / <code>ggplot2</code> / TikZ 代码并润色英文图注。</li>
        </ul>
        <a href="https://xqai.top">立即访问 XQAI 自助充值中心 ↗</a>
      </details>
    </td>
    <td width="50%" valign="top">
      <a href="#-支持作者"><strong>💖 虚位以待 · 成为赞助伙伴</strong></a><br><br>
      <sub>欢迎科研 AI 工具、云计算、API 平台及学术社区联系赞助或资源支持，共同维持开源顶刊图库持续免费开放。</sub><br><br>
      <sub>👉 <a href="#-支持作者">请作者喝杯咖啡 ☕</a> · <a href="https://daydayup-xq.github.io/ncs-paper-figure-gallery/support.html">支持与赞助页面 ↗</a></sub>
    </td>
  </tr>
</table>

<sub>赞助伙伴介绍由合作方提供，服务详情、价格与可用性以伙伴官网实时页面为准。</sub>

---

**NSC 顶刊论文主图灵感画廊**收录 **Nature、Science、Cell 三大正刊及 65 本高影响力学科学专刊** 最近三年（2024–2026）的 **5,270 张 Open Access** 论文主图（`Figure 1` 与 `Graphical Abstract`）。它是面向科研人员的构图与配色灵感索引，而不是论文评价排行。每张卡片直连原文 DOI / PMC，并自动标注出版体系、期刊级别、学科方向、视觉模式与实测 5 色色卡。

- **多维筛选与排序**：支持按 `出版体系`（Nature / Science / Cell）、`期刊级别`（★ 三大正刊 / 核心大子刊 / 综合 OA）、`年份`（2026 / 2025 / 2024）、`6 大学科`、`5 类视觉模式` 及 68 本单刊下拉组合筛选，默认正刊优先。
- **全文检索与 URL 联动**：支持标题、期刊、作者、DOI 及图注关键词检索（如 `CRISPR`、`perovskite`、`diffusion`、`single-cell`），所有筛选条件实时写入 URL（如 `?family=cell&tier=flagship&y=2026`），可直接复制分享给课题组同伴。
- **灯箱大图检视**：支持一键切换 1:1 高清放大与官方高分辨率原图（`highres`）、键盘 `←` / `→` 连续翻页、`Esc` 退出，以及 `复制 BibTeX` 与 `DOI / PMC` 原文直达。
- **实测顶刊色卡库**：每张主图均基于原图像素量化提取 5 色主色板（自动剔除纯白/纯黑底色），支持卡片内一键复制 HEX、灯箱导出 **Python / R / CSS** 代码，以及右上角 **「🎨 顶刊色卡库」** 实时汇总当前筛选配色的调色板。
- **中英双语 & 深浅色主题**：网站顶部支持一键切换 **中文 / English** 与 **☀️ / 🌙 深浅主题**，瀑布流与等高网格两种视图自由切换。
- **100% Open Access 官方 CDN 直链**：所有图片直接引用 Springer Nature、Elsevier 与 NCBI PMC Open Data (`pmc-oa-opendata`) 官方图床，保留完整署名与开源许可。

---

## 📊 收录规模

当前全库共收录 **5,270 张** 2024–2026 年 Open Access 主图，覆盖配置中的全部 **68 本** NSC 正刊与子刊：

| 出版体系 | 2024 | 2025 | 2026 | 主图合计 | ★ 三大正刊 | 核心专刊大子刊 | 综合 / 小子刊 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 🔴 **Nature Portfolio** | 467 | 634 | 1,534 | **2,635** | 1,100 | 1,505（36 本） | 30（*Nat Commun*） |
| 🟢 **Cell Press** | 365 | 481 | 973 | **1,819** | 884 | 905（21 本） | 30（*iScience* / *Cell Rep*） |
| 🔵 **Science Family** | 277 | 293 | 246 | **816** | 150 | 74（4 本） | 592（*Sci Adv*） |
| **总计** | **1,109** | **1,408** | **2,753** | **5,270** | **2,134** | **2,484** | **652** |

### 按学科方向划分

| 学科方向 | 数量 | 占比 | 核心覆盖方向与示例链接 |
|---|---:|---:|---|
| 🧬 **生命科学与医学** (`bio-med`) | **3,090** | 58.6% | 结构生物、免疫肿瘤、神经科学、单细胞、临床医学 · [浏览 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?discipline=bio-med) |
| ⚛️ **物理、光学与工程** (`phys-eng`) | **596** | 11.3% | 量子信息、光子学、柔性电子、机器人、天体物理 · [浏览 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?discipline=phys-eng) |
| ⚡ **能源、地球与环境** (`energy-env`) | **466** | 8.8% | 二次电池、光伏催化、气候变化、水资源与可持续发展 · [浏览 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?discipline=energy-env) |
| 🧪 **材料与化学纳米** (`mat-chem`) | **465** | 8.8% | 有机/无机合成、纳米催化、MOF/COF、高分子与器件化学 · [浏览 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?discipline=mat-chem) |
| 🤖 **AI 与计算科学** (`ai-comp`) | **446** | 8.5% | 科学基础模型、AI4Science、生物信息算法、计算神经 · [浏览 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?discipline=ai-comp) |
| 🌐 **交叉与行为社会** (`inter-soc`) | **207** | 3.9% | 人类行为、心理学、心理健康、城市系统与交叉学科 · [浏览 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?discipline=inter-soc) |

<details>
<summary>📚 <strong>展开查看全部 68 本已收录期刊明细</strong></summary>

- **🔴 Nature 系列（38 本 · 2,635 张）**：*Nature* (1,100) · *Nature Methods* (126) · *Nature Medicine* (106) · *Nature Physics* (91) · *Nature Human Behaviour* (81) · *Nature Machine Intelligence* (67) · *Nature Chemistry* (60) · *Nature Aging* (53) · *Nature Astronomy* (49) · *Nature Mental Health* (49) · *Nature Ecology & Evolution* (48) · *Nature Genetics* (48) · *Nature Structural & Molecular Biology* (47) · *Nature Chemical Biology* (46) · *Nature Geoscience* (46) · *Nature Photonics* (46) · *Nature Climate Change* (40) · *Nature Materials* (39) · *Nature Microbiology* (38) · *Nature Nanotechnology* (36) · *Nature Plants* (36) · *Nature Communications* (30) · *Nature Cities* (29) · *Nature Cancer* (28) · *Nature Sustainability* (28) · *Nature Computational Science* (27) · *Nature Neuroscience* (27) · *Nature Cell Biology* (26) · *Nature Cardiovascular Research* (25) · *Nature Energy* (25) · *Nature Electronics* (22) · *Nature Catalysis* (21) · *Nature Synthesis* (21) · *Nature Biotechnology* (18) · *Nature Food* (18) · *Nature Immunology* (17) · *Nature Water* (13) · *Nature Biomedical Engineering* (8)
- **🟢 Cell 系列（24 本 · 1,819 张）**：*Cell* (884) · *Patterns* (103) · *Cancer Cell* (72) · *Cell Reports Medicine* (61) · *Immunity* (51) · *Cell Genomics* (50) · *Cell Systems* (50) · *Molecular Cell* (50) · *Neuron* (49) · *Cell Stem Cell* (46) · *Current Biology* (46) · *Cell Chemical Biology* (45) · *Med* (43) · *Cell Host & Microbe* (41) · *Developmental Cell* (40) · *Cell Metabolism* (37) · *Structure* (33) · *Device* (28) · *iScience* (28) · *Joule* (21) · *Chem* (18) · *Matter* (11) · *One Earth* (10) · *Cell Reports* (2)
- **🔵 Science 系列（6 本 · 816 张）**：*Science Advances* (592) · *Science* (150) · *Science Translational Medicine* (35) · *Science Immunology* (31) · *Science Signaling* (7) · *Science Robotics* (1)

</details>

---

## 🧭 视觉模式

标签描述图的视觉表达功能，帮助按构图形式而不是仅按关键词找参考：

| 标签 | 数量 | 含义与构图参考场景 | 直达筛选 |
|---|---:|---|---|
| 🎯 `graphical-abstract` | **433** | 单图视觉摘要（GA），用一眼看懂的概览凝练研究核心发现（含大量 Cell 系 `fx1` 官方摘要图） | [筛选 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?pattern=graphical-abstract) |
| 🔬 `mechanism` | **757** | 分子结合机制、催化循环、细胞或神经信号通路示意图 | [筛选 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?pattern=mechanism) |
| 📐 `pipeline` | **554** | 端到端实验路线、系统架构、AI 模型流程或研究框架图 | [筛选 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?pattern=pipeline) |
| 🧩 `multipanel` | **2,875** | 典型顶刊 `a/b/c/d` 组合主图，兼顾概念示意与关键实验曲线/表征 | [筛选 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?pattern=multipanel) |
| 🗺️ `characterization` | **651** | 冷冻电镜分子结构、空间转录组图谱、材料微观表征及地图分布 | [筛选 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?pattern=characterization) |

---

## 🎨 实测色卡提取

点击每张卡片底部的 `PALETTE` 色块可直接复制 HEX 色号；点击右上角 **「🎨 顶刊色卡库」** 可根据当前筛选结果实时查看前 36 篇同领域顶刊论文色板并点击 `Copy Py`；在 **Lightbox 大图弹窗** 内支持直接一键导出为 **Python / R / CSS** 代码片段：

```python
# Lightbox 点击 "Python" 后直接用于 matplotlib / seaborn
import seaborn as sns
palette = ["#2b5c8f", "#c84b31", "#2e8b57", "#d98c26", "#724e98"]
sns.set_palette(palette)
```

```r
# Lightbox 点击 "R" 后直接用于 ggplot2
library(ggplot2)
palette <- c("#2b5c8f", "#c84b31", "#2e8b57", "#d98c26", "#724e98")
scale_color_manual(values = palette)
```

---

## 🚀 快速开始

在线浏览：**[GitHub Pages 在线画廊](https://daydayup-xq.github.io/ncs-paper-figure-gallery/)**

本地运行或复现采集：

```bash
git clone https://github.com/daydayup-xq/ncs-paper-figure-gallery.git
cd ncs-paper-figure-gallery

# 方式一：本地 HTTP 服务预览（或直接双击打开 index.html）
python -m http.server 8080

# 方式二：增量采集最近三年 Open Access NSC 主图（需 requests、pillow）
python -X utf8 scripts/crawl_ncs_figures.py --merge --target-total 5500 --workers 32
python -X utf8 scripts/validate_gallery.py
```

- **每月自动更新**：仓库内置 [`.github/workflows/update-figures.yml`](.github/workflows/update-figures.yml) 与 [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml)，每月 1 日 03:00 UTC（北京时间 11:00）自动增量采集最新 OA 主图并发布新版 **GitHub Pages**。

## 🗃️ 仓库结构

```text
├── index.html                  # 画廊主页（多维筛选 / 瀑布流 / 灯箱 / 配色库 / 支持作者弹窗）
├── support.html                # 独立赞赏支持与赞助伙伴页面（中英双语）
├── README.md / README.en.md    # 中英文项目文档
├── assets/
│   ├── style.css / app.js      # 样式与前端交互逻辑
│   ├── i18n.js                 # 中英文切换词典
│   ├── figures.js              # 前端内联数据集（由 data/figures.json 同步生成）
│   └── wechat-pay.jpg          # 作者赞赏收款码
├── data/
│   ├── journals.json           # 68 本 NSC 期刊配置与学科映射表
│   └── figures.json            # 全量 5,270 条 OA 主图权威清单
├── docs/                       # 项目横幅与赞助伙伴视觉资产
├── scripts/
│   ├── crawl_ncs_figures.py    # OpenAlex + NCBI E-Utilities + 官方 CDN 采集与色板提取管线
│   └── validate_gallery.py     # 数据完整性、尺寸、色板与静态资源校验
└── .github/workflows/          # Pages 部署与每月定时增量更新工作流
```

## ⚠️ 版权

论文元数据来自 [OpenAlex](https://openalex.org/) 与 [NCBI E-Utilities](https://www.ncbi.nlm.nih.gov/books/NBK25500/)，所有图像均直接外链自 Springer Nature (`media.springernature.com`)、Elsevier (`ars.els-cdn.com`) 与 AWS Open Data `pmc-oa-opendata` (`pmc-oa-opendata.s3.amazonaws.com`)。图片版权归原作者及各自出版方所有，仅作非商业科研学习与版式参考索引，遵循原论文对应的 CC BY / Open Access 协议；本站前端与工具代码采用 [MIT License](LICENSE) 开源。

## 📌 引用

```bibtex
@misc{nsc_paper_figure_gallery,
  title  = {NSC Paper Figure Gallery: An All-Discipline Open Access Gallery of Figure 1 and Graphical Abstracts from Nature, Science, and Cell (2024--2026)},
  year   = {2026},
  url    = {https://github.com/daydayup-xq/ncs-paper-figure-gallery}
}
```

<details>
<summary><strong>🖼️ 精选图录（Nature · Cell · Science 2026 示例）</strong></summary>

完整 5,270 张主图请访问 [在线画廊](https://daydayup-xq.github.io/ncs-paper-figure-gallery/)。以下图片均直链自出版商或 PMC 官方 Open Access 图床，点击标题可跳转原论文：

| <a href="https://doi.org/10.1038/s41586-025-09064-1"><img src="https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fs41586-025-09064-1/MediaObjects/41586_2025_9064_Fig1_HTML.png" width="230"></a><br><sub><strong>Nature</strong> (2026) · <a href="https://doi.org/10.1038/s41586-025-09064-1">Tracing the spread of Germanic languages using ancient genomics</a></sub> | <a href="https://doi.org/10.1016/j.cell.2026.01.026"><img src="https://ars.els-cdn.com/content/image/1-s2.0-S0092867426001133-gr1.jpg" width="230"></a><br><sub><strong>Cell</strong> (2026) · <a href="https://doi.org/10.1016/j.cell.2026.01.026">PLANeT: Understanding and leveraging the genome of land plants for a sustainable future</a></sub> | <a href="https://doi.org/10.1126/science.adx4174"><img src="https://pmc-oa-opendata.s3.amazonaws.com/PMC12850507.1/nihms-2134378-f0001.jpg" width="230"></a><br><sub><strong>Science</strong> (2026) · <a href="https://doi.org/10.1126/science.adx4174">Inherited resilience to clonal hematopoiesis by modifying stem cell RNA regulation</a></sub> |
|---|---|---|
| <a href="https://doi.org/10.1038/s43587-026-01125-y"><img src="https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fs43587-026-01125-y/MediaObjects/43587_2026_1125_Fig1_HTML.png" width="230"></a><br><sub><strong>Nature Aging</strong> (2026) · <a href="https://doi.org/10.1038/s43587-026-01125-y">A unifying model of stem cell dynamics explains age-related methylation patterns across mammals</a></sub> | <a href="https://doi.org/10.1016/j.ccell.2026.05.008"><img src="https://ars.els-cdn.com/content/image/1-s2.0-S1535610826002539-gr1.jpg" width="230"></a><br><sub><strong>Cancer Cell</strong> (2026) · <a href="https://doi.org/10.1016/j.ccell.2026.05.008">Pathogenesis of diffuse large B cell lymphoma proteogenotypes</a></sub> | <a href="https://doi.org/10.1126/sciimmunol.ads9407"><img src="https://pmc-oa-opendata.s3.amazonaws.com/PMC12922763.1/nihms-2138343-f0001.jpg" width="230"></a><br><sub><strong>Science Immunology</strong> (2026) · <a href="https://doi.org/10.1126/sciimmunol.ads9407">The OAS–RNase L pathway: Insights from experiments of nature</a></sub> |

</details>

## ♡ 支持作者

### 请作者喝杯咖啡 ☕

如果这个画廊帮你找到了顶刊论文配图与配色灵感，欢迎随意支持，帮助我持续整理主图、更新数据和维护工具。

<table>
  <tr>
    <td align="center" valign="top"><strong>微信支付</strong><br><a href="assets/wechat-pay.jpg"><img src="assets/wechat-pay.jpg" alt="微信收款码，点击查看原图" width="220"></a></td>
    <td align="center" valign="top"><strong>赞助伙伴 · XQAI</strong><br><a href="https://xqai.top"><img src="docs/xqai-banner.svg" alt="XQAI AI 会员自助充值中心" width="320"></a><br><br><sub>ChatGPT Plus / Pro 24h 全自动自助充值：<a href="https://xqai.top"><strong>https://xqai.top ↗</strong></a></sub></td>
  </tr>
</table>

<sub>点击微信收款码可查看原图；手机浏览可保存图片，在微信扫一扫中从相册选择。也可访问网页端 <a href="https://daydayup-xq.github.io/ncs-paper-figure-gallery/support.html">支持页面 ↗</a>。</sub>

打赏完全自愿，金额随意。感谢你的支持，点个 **Star**、分享给同伴和提 Issue 反馈也同样重要。
