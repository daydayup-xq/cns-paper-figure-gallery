<div align="center">

# 🔬 NCS Paper Figure Gallery · Nature · Science · Cell 顶刊主图与配色灵感库

**面向全学科科研人员的顶刊首图（Figure 1）与视觉摘要（Graphical Abstract）检索、构图对标与实测色板提取平台（2024–2026 Open Access）**

[![Live Site](https://img.shields.io/badge/🌐%20在线访问-NCS%20Figure%20Gallery-2563eb?style=for-the-badge)](https://daydayup-xq.github.io/ncs-paper-figure-gallery/)
[![Total Figures](https://img.shields.io/badge/🖼️%20收录主图-5%2C270%2B%20OA-0f172a?style=for-the-badge)](https://daydayup-xq.github.io/ncs-paper-figure-gallery/)
[![Nature Portfolio](https://img.shields.io/badge/Nature%20系-2%2C635-c8102e?style=for-the-badge)](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?family=nature)
[![Cell Press](https://img.shields.io/badge/Cell%20系-1%2C819-047857?style=for-the-badge)](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?family=cell)
[![Science Family](https://img.shields.io/badge/Science%20系-816-1d4ed8?style=for-the-badge)](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?family=science)
[![Flagship Papers](https://img.shields.io/badge/★%20三大正刊-2%2C134-d97706?style=for-the-badge)](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?tier=flagship)
[![Years](https://img.shields.io/badge/📅%20收录年份-2024–2026-475569?style=for-the-badge)](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?y=2026)
[![Auto Update](https://img.shields.io/badge/🔄%20每月自动更新-GitHub%20Actions-16a34a?style=for-the-badge)](.github/workflows/update-figures.yml)

[🌐 在线访问网站](https://daydayup-xq.github.io/ncs-paper-figure-gallery/) ·
[🧭 网站使用指南](#-网站使用指南5-步搞定顶刊配图与配色) ·
[🎨 色卡提取教程](#第四步一键提取顶刊实测色板hex--python--r--css) ·
[📊 收录规模](#-数据集收录规模5270-张--68-本期刊) ·
[🤝 科研 AI 充值 (xqai.top)](#-科研-ai-助手自助充值推荐--xqai)

</div>

---

> 💡 **为什么做这个网站？**
> 画论文 **Figure 1** 或 **Graphical Abstract** 时，最怕“没参考构图、配色土气、不同子刊风格混搭”。
> **NCS Paper Figure Gallery** 收录了 **Nature、Science、Cell 三大正刊及 65 本子刊** 最近三年（**2024–2026**）的 **5,270 张真实 Open Access 论文主图**，按**出版体系 × 期刊级别 × 6 大全学科 × 5 类视觉范式**即时检索，并从每张顶刊原图中像素级量化提取 **5 色实测色板**——打开网页就能**对标标杆构图、一键复制 Python / R 配色代码、直达原文与 BibTeX**。

---

## 🤝 科研 AI 助手自助充值推荐 — XQAI

<table>
  <tr>
    <td width="100%" valign="top">
      <h3><a href="https://xqai.top">⚡ XQAI · AI 会员自助充值中心（https://xqai.top）</a></h3>
      <p><b>ChatGPT Plus 充值 · ChatGPT Pro 会员开通 · 24 小时全自动自助到账</b></p>
      <ul>
        <li><b>🔐 账号安全无需代充</b>：全程官方卡密自助充值，<b>无需向第三方提供账号密码</b>，避免手工代充导致封号或降智风险，研究人员可放心长期使用。</li>
        <li><b>⏱️ 24 小时自助秒充</b>：支持 ChatGPT Plus / Pro 会员自助开通与续费，适合文献精读、科研绘图与基金写作高峰期随时使用。</li>
        <li><b>🎨 搭配 NCS 图库的顶刊作图工作流</b>：在本站挑好对标期刊的 <code>Figure 1</code> 排版范式并一键复制 <code>Python / R</code> 实测 HEX 色卡后，可直接让 ChatGPT Plus / Pro 根据该色板与排版逻辑生成可复用的 <code>matplotlib</code> / <code>ggplot2</code> / TikZ 绘图代码，并辅助润色论文 Figure Caption。</li>
      </ul>
      <p>👉 <b>立即访问自助充值平台：<a href="https://xqai.top">https://xqai.top</a></b></p>
    </td>
  </tr>
</table>

---

## 🧭 网站使用指南：5 步搞定顶刊配图与配色

访问在线画廊 **https://daydayup-xq.github.io/ncs-paper-figure-gallery/** ，无需登录、纯静态秒开，支持 **中文 / English 双语切换** 与 **浅色 / 深色（☀️ / 🌙）模式**。

### 第一步：按「出版体系 + 期刊级别」锁定投稿标杆

网站顶部筛选栏提供 **三大出版体系** 与 **三级期刊权重矩阵**，默认按 **「正刊优先 → 年份（2026 → 2024）」** 排序：

| 筛选维度 | 选项说明 | 适用使用场景 | 直达快捷链接 |
|---|---|---|---|
| **出版体系** | `Nature 系` · `Science 系` · `Cell 系` | 对标目标投稿出版社的字体留白、子图编号风格（如 Nature 小写粗体 `a, b, c` vs Science 大写 `A, B, C` vs Cell GA 信息密度） | [Nature](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?family=nature) · [Science](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?family=science) · [Cell](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?family=cell) |
| **期刊级别** | `★ 三大正刊 (N/S/C)` · `核心大子刊` · `综合/小子刊 (NC/SciAdv/CR)` | **正刊**看顶层宏观叙事；**60+ 核心大子刊**看专科方法与机理深度；**NC / SciAdv / Cell Rep / iScience** 看高产出实战排版 | [★ 三大正刊](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?tier=flagship) · [核心大子刊](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?tier=subjournal) · [综合/小子刊](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?tier=oa-series) |
| **单刊精确筛选** | 搜索栏右侧「全部期刊」下拉框 | 直接定位某一本特定期刊（共 68 本，按收录篇数排序，如 *Nature Methods*、*Cancer Cell*、*Science Advances*、*Joule*） | [全部期刊](https://daydayup-xq.github.io/ncs-paper-figure-gallery/) |
| **年份筛选** | `2026` · `2025` · `2024` | 追踪最新一年顶刊审美趋势与热点视觉表达 | [2026](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?y=2026) · [2025](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?y=2025) · [2024](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?y=2024) |

---

### 第二步：按「6 大全学科方向」对标同领域视觉习惯

针对 *Nature*、*Science*、*Nature Communications*、*Science Advances*、*iScience* 等综合刊物，网站会结合论文标题、摘要与 OpenAlex 学科主题将其自动路由到以下 **6 大科研方向**：

- 🧬 **生命科学与医学**（`bio-med`，3,090 张）：结构生物学、免疫肿瘤、神经回路、单细胞与临床研究（[浏览 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?discipline=bio-med)）
- ⚛️ **物理、光学与工程**（`phys-eng`，596 张）：量子计算、超构表面、光子芯片、柔性电子与机器人（[浏览 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?discipline=phys-eng)）
- ⚡ **能源、地球与环境**（`energy-env`，466 张）：二次电池、钙钛矿光伏、电催化、碳中和与气候地球系统（[浏览 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?discipline=energy-env)）
- 🧪 **材料与化学纳米**（`mat-chem`，465 张）：催化循环、MOF/COF、有机合成、二维材料与超分子自组装（[浏览 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?discipline=mat-chem)）
- 🤖 **AI 与计算科学**（`ai-comp`，446 张）：科学基础模型、AI4Science、生物信息算法架构与计算模拟（[浏览 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?discipline=ai-comp)）
- 🌐 **交叉与行为社会**（`inter-soc`，207 张）：人类行为、城市可持续、认知神经与计算社会科学（[浏览 ↗](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?discipline=inter-soc)）

---

### 第三步：按「5 类主图视觉范式」解决构图卡壳

不知道 Figure 1 应该画成流程图、机制图还是多面板数据图？直接按视觉类型筛选：

| 主图类型标签 | 对应范式 | 当前收录 | 什么时候优先选这类图作参考？ |
|---|---|---:|---|
| 🎯 **视觉摘要 GA** (`graphical-abstract`) | Graphical Abstract | **433** | Cell Press 等期刊首图总览，一图讲清核心科学问题、技术手段与结论（多来自 Cell 系官方 `fx1` 高清摘要图） |
| 🔬 **机理与通路** (`mechanism`) | Mechanism & Pathway | **757** | 需要绘制分子结合机制、催化循环路径、细胞/神经信号通路或物理机理示意图时 |
| 📐 **实验/算法流程** (`pipeline`) | Workflow & Pipeline | **554** | 需要展示“样本采集 → 建模/实验干预 → 评估输出”或深度学习框架（Architecture / Framework）时 |
| 🧩 **多面板主图** (`multipanel`) | Multi-Panel Teaser | **2,875** | 最典型的顶刊 `a/b/c/d` 混合主图：左侧放科学假说或原理图，右侧排布关键表征图、热图或统计验证图 |
| 🗺️ **结构与空间图谱** (`characterization`) | Structure & Atlas | **651** | 冷冻电镜分子结构、空间转录组 UMAP / 组织图谱、TEM/SEM 材料形貌及全球地理分布地图 |

---

### 第四步：一键提取顶刊实测色板（HEX / Python / R / CSS）

每张主图卡片都附带从该图真实像素中量化提取并去除纯白/纯黑底色的 **5 色主色板**：

1. **卡片快捷复制**：直接点击任意卡片底部 `PALETTE` 行的 5 个色块，立即复制对应 HEX 色号（如 `#2b5c8f`），页面底部会出现 Toast 提示。
2. **「🎨 顶刊色卡库」批量灵感**：先通过筛选器锁定你想模仿的领域（例如 `Nature 系` + `🧪 材料与化学纳米` + `2026`），再点击右上角 **「🎨 顶刊色卡库」**，弹窗会实时汇总当前筛选下前 36 张顶刊原图的实测色卡；支持点击单色复制 HEX，或点击卡片右下角 **`Copy Py`** 直接复制 Python 列表。
3. **Lightbox 三语言代码导出**：点击任意图片进入大图检视后，点击右上角调色盘的 **`Python`**、**`R`** 或 **`CSS`** 按钮即可一键复制对应代码：

```python
# 在 Lightbox 点击 "Python" 或在顶刊色卡库点击 "Copy Py" 复制后，直接用于 matplotlib / seaborn：
import matplotlib.pyplot as plt
import seaborn as sns

palette = ["#2b5c8f", "#c84b31", "#2e8b57", "#d98c26", "#724e98"]  # 示例为图库实测提取格式
sns.set_palette(palette)
```

```r
# 在 Lightbox 点击 "R" 复制后，直接用于 ggplot2：
library(ggplot2)

palette <- c("#2b5c8f", "#c84b31", "#2e8b57", "#d98c26", "#724e98")
scale_color_manual(values = palette)
```

---

### 第五步：大图 1:1 检视、URL 分享与 BibTeX 引用

- **Lightbox 大图检视**：点击任意卡片打开高清原图视图，自动后台无感知切换期刊官方高分辨率版本（`highres`）；点击图片或 **`🔍 1:1`** 按钮可切换 1:1 像素级缩放，支持键盘 `←` / `→` 连续浏览前后主图、`Esc` 关闭弹窗。
- **科研常用功能一应俱全**：弹窗内完整显示图片像素宽高（`W × H px`）、Figure 标签与完整图注（Caption）、作者列表、被引数、`📄 高清原图 ↗`、`🔗 DOI 官网 ↗`、`📖 PMC 阅读 ↗` 及一键 **`复制 BibTeX`**。
- **搜索与排序技巧**：顶部搜索框支持检索**论文标题、期刊名称、图注关键词（如 `CRISPR`、`perovskite`、`diffusion`、`single-cell`）、作者姓名或 DOI**；右侧可切换 **`正刊优先 → 年份`** / **`最新年份 → 级别`** / **`引用数从高到低`** / **`标题 A–Z`**，以及 **`瀑布流`** / **`等高网格`** 布局。
- **URL 筛选状态分享**：页面所有筛选操作都会实时同步至地址栏参数，复制 URL 发给课题组同伴或导师即可直接复现完全一致的筛选视图，支持的参数包括：
  `y`（年份）、`family`（出版体系）、`tier`（期刊级别）、`discipline`（学科方向）、`pattern`（主图类型）、`journal`（期刊 slug）、`q`（检索词）、`sort`（排序方式）。  
  示例：[`?family=cell&tier=flagship&y=2026`](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?family=cell&tier=flagship&y=2026) · [`?family=science&discipline=bio-med`](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?family=science&discipline=bio-med) · [`?pattern=graphical-abstract`](https://daydayup-xq.github.io/ncs-paper-figure-gallery/?pattern=graphical-abstract)

---

## 📊 数据集收录规模（5,270 张 · 68 本期刊）

> 当前全库 **5,270 张** Open Access 主图（2024–2026），全部来自真实论文并直连出版商/PMC 官方图床 CDN。

### 按「出版体系 × 期刊级别」统计

| 出版体系 | ★ 三大正刊 (`Flagship`) | 核心大子刊 (`Major Sub-journals`) | 综合 / 小子刊 (`Broad OA`) | 体系合计 |
|---|---:|---:|---:|---:|
| 🔴 **Nature Portfolio** (`nature`) | **1,100** (*Nature*) | **1,505**（36 本专刊） | **30** (*Nature Communications*) | **2,635** |
| 🟢 **Cell Press** (`cell`) | **884** (*Cell*) | **905**（21 本专刊） | **30** (*iScience* 28 + *Cell Reports* 2) | **1,819** |
| 🔵 **Science Family** (`science`) | **150** (*Science*) | **74**（4 本专刊） | **592** (*Science Advances*) | **816** |
| **合计** | **2,134** | **2,484** | **652** | **5,270** |

### 按「出版年份」与「学科方向」统计

| 年份 | 主图数量 | 占比 | | 学科方向 | 主图数量 | 占比 |
|---|---:|---:|---|---|---:|---:|
| **2026** | 2,753 | 52.2% | | 🧬 生命科学与医学 (`bio-med`) | 3,090 | 58.6% |
| **2025** | 1,408 | 26.7% | | ⚛️ 物理、光学与工程 (`phys-eng`) | 596 | 11.3% |
| **2024** | 1,109 | 21.0% | | ⚡ 能源、地球与环境 (`energy-env`) | 466 | 8.8% |
| | | | | 🧪 材料与化学纳米 (`mat-chem`) | 465 | 8.8% |
| | | | | 🤖 AI 与计算科学 (`ai-comp`) | 446 | 8.5% |
| | | | | 🌐 交叉与行为社会 (`inter-soc`) | 207 | 3.9% |

<details>
<summary>📚 <b>展开查看已收录全部 68 本期刊明细表（全部 68 本均已覆盖真图）</b></summary>

#### 🔴 Nature Portfolio（共 38 本 · 2,635 张）
- **正刊（1,100）**：*Nature* (1,100)
- **核心大子刊（1,505）**：*Nature Methods* (126), *Nature Medicine* (106), *Nature Physics* (91), *Nature Human Behaviour* (81), *Nature Machine Intelligence* (67), *Nature Chemistry* (60), *Nature Aging* (53), *Nature Astronomy* (49), *Nature Mental Health* (49), *Nature Ecology & Evolution* (48), *Nature Genetics* (48), *Nature Structural & Molecular Biology* (47), *Nature Chemical Biology* (46), *Nature Geoscience* (46), *Nature Photonics* (46), *Nature Climate Change* (40), *Nature Materials* (39), *Nature Microbiology* (38), *Nature Nanotechnology* (36), *Nature Plants* (36), *Nature Cities* (29), *Nature Cancer* (28), *Nature Sustainability* (28), *Nature Computational Science* (27), *Nature Neuroscience* (27), *Nature Cell Biology* (26), *Nature Cardiovascular Research* (25), *Nature Energy* (25), *Nature Electronics* (22), *Nature Catalysis* (21), *Nature Synthesis* (21), *Nature Biotechnology* (18), *Nature Food* (18), *Nature Immunology* (17), *Nature Water* (13), *Nature Biomedical Engineering* (8)
- **综合 / 小子刊（30）**：*Nature Communications* (30)

#### 🟢 Cell Press（共 24 本 · 1,819 张）
- **正刊（884）**：*Cell* (884)
- **核心大子刊（905）**：*Patterns* (103), *Cancer Cell* (72), *Cell Reports Medicine* (61), *Immunity* (51), *Cell Genomics* (50), *Cell Systems* (50), *Molecular Cell* (50), *Neuron* (49), *Cell Stem Cell* (46), *Current Biology* (46), *Cell Chemical Biology* (45), *Med* (43), *Cell Host & Microbe* (41), *Developmental Cell* (40), *Cell Metabolism* (37), *Structure* (33), *Device* (28), *Joule* (21), *Chem* (18), *Matter* (11), *One Earth* (10)
- **综合 / 小子刊（30）**：*iScience* (28), *Cell Reports* (2)

#### 🔵 Science Family（共 6 本 · 816 张）
- **正刊（150）**：*Science* (150)
- **核心大子刊（74）**：*Science Translational Medicine* (35), *Science Immunology* (31), *Science Signaling* (7), *Science Robotics* (1)
- **综合 / 小子刊（592）**：*Science Advances* (592)

</details>

---

## ⚙️ 本地运行与自动月度更新说明

本项目为**纯静态前端 + Python 增量采集脚本**结构，不依赖数据库或后端服务器：

```bash
# 1. 克隆仓库并本地启动预览（或在浏览器直接打开 index.html）
git clone https://github.com/daydayup-xq/ncs-paper-figure-gallery.git
cd ncs-paper-figure-gallery
python -m http.server 8080

# 2. 按需增量抓取并扩展最近三年（2024–2026）OA 论文主图（需 requests、pillow）
python -X utf8 scripts/crawl_ncs_figures.py --families science cell --merge --target-total 5500 --workers 32

# 3. 校验数据集完整性、尺寸、色板及前端资源
python -X utf8 scripts/validate_gallery.py
```

- **自动更新机制**：仓库内置 [`.github/workflows/update-figures.yml`](.github/workflows/update-figures.yml) 与 [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml)，每月 1 日 03:00 UTC（北京时间 11:00，`0 3 1 * *`）自动采集最新开放获取的 NCS 论文主图并重新部署 **GitHub Pages**。
- **Open Access 版权声明**：论文元数据来自 [OpenAlex](https://openalex.org/) 与 [NCBI E-Utilities](https://www.ncbi.nlm.nih.gov/books/NBK25500/)，图像资产直接通过链接引用自 Springer Nature (`media.springernature.com`)、Elsevier (`ars.els-cdn.com`) 与 AWS Open Data `pmc-oa-opendata` (`pmc-oa-opendata.s3.amazonaws.com`)。所有论文主图版权归原作者与出版商所有，遵循各自 CC BY / Open Access 许可协议；本网站代码基于 MIT License 开源。
