(function () {
  "use strict";

  const ALL_FIGURES = Array.isArray(window.FIGURES) ? window.FIGURES : [];
  const META = window.GALLERY_META || {};
  const PAGE_SIZE = 40;
  const LAYOUT_MODES = ["masonry", "grid", "compact"];

  let masonryCols = [];
  let masonryHeights = [];
  let currentColCount = 0;
  let scrollCheckScheduled = false;

  const savedLayout = localStorage.getItem("cns_layout") || localStorage.getItem("ncs_layout");
  const state = {
    lang: localStorage.getItem("cns_lang") || localStorage.getItem("ncs_lang") || "zh",
    theme: localStorage.getItem("cns_theme") || localStorage.getItem("ncs_theme") || "light",
    layout: LAYOUT_MODES.includes(savedLayout) ? savedLayout : "masonry",
    filtersCollapsed: localStorage.getItem("cns_filters_collapsed") === "1",
    q: "",
    family: "all",
    tier: "all",
    year: "all",
    discipline: "all",
    pattern: "all",
    journal: "all",
    sort: "tier",
    renderedCount: 0,
    filtered: [],
    lbIndex: -1,
  };

  const els = {
    gallery: document.getElementById("gallery"),
    sentinel: document.getElementById("sentinel"),
    endHint: document.getElementById("end-hint"),
    empty: document.getElementById("empty"),
    search: document.getElementById("search"),
    clearSearch: document.getElementById("clear-search"),
    resultCount: document.getElementById("result-count"),
    activeFilterTags: document.getElementById("active-filter-tags"),
    sort: document.getElementById("sort"),
    journalFilter: document.getElementById("journal-filter"),
    viewSwitch: document.getElementById("view-switch"),
    densityToggle: document.getElementById("density-toggle"),
    densityLabel: document.getElementById("density-label"),
    toggleFiltersBtn: document.getElementById("toggle-filters-btn"),
    filterMatrix: document.getElementById("filter-matrix"),
    resetTop: document.getElementById("reset-top"),
    resetAll: document.getElementById("reset-all"),
    quickStatPills: document.querySelectorAll("#hero-stats .stat-pill"),
    topicChips: document.querySelectorAll(".topic-chip"),
    familyChips: document.getElementById("family-chips"),
    tierChips: document.getElementById("tier-chips"),
    yearChips: document.getElementById("year-chips"),
    disciplineChips: document.getElementById("discipline-chips"),
    patternChips: document.getElementById("pattern-chips"),
    langToggle: document.getElementById("lang-toggle"),
    themeToggle: document.getElementById("theme-toggle"),
    paletteStudioBtn: document.getElementById("palette-studio-btn"),
    supportBtn: document.getElementById("support-btn"),
    footerUpdated: document.getElementById("footer-updated"),
    toast: document.getElementById("toast"),
    lb: document.getElementById("lightbox"),
    lbBackdrop: document.getElementById("lb-backdrop"),
    lbClose: document.getElementById("lb-close"),
    lbPrev: document.getElementById("lb-prev"),
    lbNext: document.getElementById("lb-next"),
    lbImgWrap: document.getElementById("lb-img-wrap"),
    lbImg: document.getElementById("lb-img"),
    lbZoom: document.getElementById("lb-zoom"),
    lbFamily: document.getElementById("lb-family"),
    lbTier: document.getElementById("lb-tier"),
    lbYear: document.getElementById("lb-year"),
    lbDiscipline: document.getElementById("lb-discipline"),
    lbPattern: document.getElementById("lb-pattern"),
    lbLicense: document.getElementById("lb-license"),
    lbTitle: document.getElementById("lb-title"),
    lbJournalMeta: document.getElementById("lb-journal-meta"),
    lbAuthors: document.getElementById("lb-authors"),
    lbFigLabel: document.getElementById("lb-fig-label"),
    lbDims: document.getElementById("lb-dims"),
    lbCaption: document.getElementById("lb-caption"),
    lbPaletteTitle: document.getElementById("lb-palette-title"),
    lbPalette: document.getElementById("lb-palette"),
    lbLayoutNotes: document.getElementById("lb-layout-notes"),
    lbCopyPy: document.getElementById("lb-copy-py"),
    lbCopyR: document.getElementById("lb-copy-r"),
    lbCopyCss: document.getElementById("lb-copy-css"),
    lbViewImage: document.getElementById("lb-view-image"),
    lbOpenPaper: document.getElementById("lb-open-paper"),
    lbOpenPmc: document.getElementById("lb-open-pmc"),
    lbAgentJson: document.getElementById("lb-agent-json"),
    lbCopyBib: document.getElementById("lb-copy-bib"),
    pm: document.getElementById("palette-modal"),
    pmBackdrop: document.getElementById("pm-backdrop"),
    pmClose: document.getElementById("pm-close"),
    pmGrid: document.getElementById("pm-grid"),
    sm: document.getElementById("support-modal"),
    smBackdrop: document.getElementById("sm-backdrop"),
    smClose: document.getElementById("sm-close"),
  };

  function t(key) {
    const dict = (window.I18N && window.I18N[state.lang]) || {};
    return dict[key] || key;
  }

  function isCurated(fig) {
    return Boolean(
      fig &&
      fig.palette_curated &&
      fig.palette_curated.status === "verified" &&
      fig.palette_curated.roles &&
      Array.isArray(fig.palette_curated.roles.primary) &&
      fig.palette_curated.roles.primary.length > 0
    );
  }

  function getCuratedSwatches(fig, includeBackground) {
    if (!isCurated(fig)) return [];
    const roles = fig.palette_curated.roles;
    const accentUpper = roles.accent ? String(roles.accent).toUpperCase() : "";
    const swatches = [];
    const seen = new Set();

    (roles.primary || []).forEach((hex) => {
      const norm = String(hex).toUpperCase();
      if (!norm || seen.has(norm)) return;
      seen.add(norm);
      const isAccentAlso = Boolean(accentUpper && norm === accentUpper);
      swatches.push({
        hex: norm,
        role: "primary",
        roleLabel: isAccentAlso
          ? `${t("curated.role.primary")}·${t("curated.role.accent")}`
          : t("curated.role.primary"),
      });
    });

    if (accentUpper && !seen.has(accentUpper)) {
      seen.add(accentUpper);
      swatches.push({
        hex: accentUpper,
        role: "accent",
        roleLabel: t("curated.role.accent"),
      });
    }

    if (roles.neutral) {
      const neutralNorm = String(roles.neutral).toUpperCase();
      if (!seen.has(neutralNorm)) {
        seen.add(neutralNorm);
        swatches.push({
          hex: neutralNorm,
          role: "neutral",
          roleLabel: t("curated.role.neutral"),
        });
      }
    }

    if (includeBackground && roles.background) {
      swatches.push({
        hex: String(roles.background).toUpperCase(),
        role: "background",
        roleLabel: t("curated.role.background"),
      });
    }

    return swatches;
  }

  function getEffectivePaletteHexes(fig) {
    if (isCurated(fig)) {
      return getCuratedSwatches(fig, false).map((s) => s.hex);
    }
    return Array.isArray(fig && fig.palette) ? fig.palette : [];
  }

  function getAgentItemUrl(fig) {
    return `api/v1/items/${encodeURIComponent(fig.id)}.json`;
  }

  function getDeepLinkFigureId() {
    const h = window.location.hash || "";
    if (h.startsWith("#fig=")) {
      try {
        return decodeURIComponent(h.slice(5));
      } catch {
        return h.slice(5);
      }
    }
    const p = new URLSearchParams(window.location.search);
    return p.get("id") || "";
  }

  function showToast(msg) {
    els.toast.textContent = msg;
    els.toast.hidden = false;
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(() => {
      els.toast.hidden = true;
    }, 1800);
  }

  function copyText(text, label) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => showToast(t("copied") + (label || text)));
    } else {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      ta.remove();
      showToast(t("copied") + (label || text));
    }
  }

  function applyTheme() {
    document.documentElement.setAttribute("data-theme", state.theme);
    els.themeToggle.textContent = state.theme === "dark" ? "☀️" : "🌙";
  }

  function applyLayout() {
    if (state.layout === "grid") {
      els.gallery.className = "grid-view";
    } else if (state.layout === "compact") {
      els.gallery.className = "compact-view";
    } else {
      els.gallery.className = "masonry";
    }
    if (els.densityLabel) {
      els.densityLabel.textContent = t(`layout.${state.layout}`);
    }
    if (els.viewSwitch) {
      els.viewSwitch.querySelectorAll(".view-tab").forEach((btn) => {
        btn.classList.toggle("active", btn.getAttribute("data-layout") === state.layout);
      });
    }
  }

  function applyFiltersCollapseState() {
    if (!els.filterMatrix || !els.toggleFiltersBtn) return;
    els.filterMatrix.hidden = state.filtersCollapsed;
    els.toggleFiltersBtn.setAttribute("aria-expanded", String(!state.filtersCollapsed));
    els.toggleFiltersBtn.textContent = state.filtersCollapsed
      ? t("btn.expandFilters")
      : t("btn.collapseFilters");
  }

  function getMasonryColumnCount() {
    const w = window.innerWidth;
    if (w <= 580) return 1;
    if (w <= 920) return 2;
    if (w <= 1320) return 3;
    return 4;
  }

  function resetGalleryContainer() {
    els.gallery.innerHTML = "";
    masonryCols = [];
    masonryHeights = [];
    if (state.layout === "masonry") {
      currentColCount = getMasonryColumnCount();
      for (let i = 0; i < currentColCount; i++) {
        const col = document.createElement("div");
        col.className = "masonry-col";
        els.gallery.appendChild(col);
        masonryCols.push(col);
        masonryHeights.push(0);
      }
    } else {
      currentColCount = 0;
    }
  }

  function applyTranslations() {
    document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      el.textContent = t(key);
    });
    document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
      el.setAttribute("placeholder", t(el.getAttribute("data-i18n-ph")));
    });
    applyLayout();
    applyFiltersCollapseState();
  }

  function readQueryParams() {
    const p = new URLSearchParams(window.location.search);
    if (p.get("y")) state.year = p.get("y");
    if (p.get("family")) state.family = p.get("family");
    if (p.get("tier")) state.tier = p.get("tier");
    if (p.get("discipline")) state.discipline = p.get("discipline");
    if (p.get("pattern")) state.pattern = p.get("pattern");
    if (p.get("journal")) state.journal = p.get("journal");
    if (p.get("q")) {
      state.q = p.get("q");
      els.search.value = state.q;
    }
    if (p.get("sort")) {
      state.sort = p.get("sort");
      els.sort.value = state.sort;
    }
  }

  function syncQueryParams() {
    const p = new URLSearchParams();
    if (state.year !== "all") p.set("y", state.year);
    if (state.family !== "all") p.set("family", state.family);
    if (state.tier !== "all") p.set("tier", state.tier);
    if (state.discipline !== "all") p.set("discipline", state.discipline);
    if (state.pattern !== "all") p.set("pattern", state.pattern);
    if (state.journal !== "all") p.set("journal", state.journal);
    if (state.q.trim()) p.set("q", state.q.trim());
    if (state.sort !== "tier") p.set("sort", state.sort);
    const qs = p.toString();
    const hash = window.location.hash || "";
    const nextUrl = qs ? `${window.location.pathname}?${qs}${hash}` : `${window.location.pathname}${hash}`;
    window.history.replaceState(null, "", nextUrl);
  }

  function updateHeroStats() {
    const cell = ALL_FIGURES.filter((f) => f.family === "cell").length;
    const nat = ALL_FIGURES.filter((f) => f.family === "nature").length;
    const sci = ALL_FIGURES.filter((f) => f.family === "science").length;
    const flag = ALL_FIGURES.filter((f) => f.tier === "flagship").length;

    document.getElementById("stat-total").textContent = ALL_FIGURES.length.toLocaleString();
    document.getElementById("stat-cell").textContent = cell.toLocaleString();
    document.getElementById("stat-nature").textContent = nat.toLocaleString();
    document.getElementById("stat-science").textContent = sci.toLocaleString();
    document.getElementById("stat-flagship").textContent = flag.toLocaleString();

    if (META.updated_at) {
      els.footerUpdated.textContent = META.updated_at.replace("T", " ").replace("Z", " UTC");
    }
  }

  function syncQuickPillsAndTopics() {
    els.quickStatPills.forEach((btn) => {
      const qFam = btn.getAttribute("data-quick-family");
      const qTier = btn.getAttribute("data-quick-tier");
      if (qFam) {
        if (qFam === "all") {
          btn.classList.toggle("active", state.family === "all" && state.tier === "all");
        } else {
          btn.classList.toggle("active", state.family === qFam);
        }
      } else if (qTier) {
        btn.classList.toggle("active", state.tier === qTier);
      }
    });

    const curQ = state.q.trim().toLowerCase();
    els.topicChips.forEach((chip) => {
      const topic = (chip.getAttribute("data-topic") || "").toLowerCase();
      chip.classList.toggle("active", Boolean(topic) && curQ === topic);
    });
  }

  function buildJournalDropdown() {
    const counts = new Map();
    ALL_FIGURES.forEach((f) => counts.set(f.journal_slug, (counts.get(f.journal_slug) || 0) + 1));
    const names = new Map();
    ALL_FIGURES.forEach((f) => names.set(f.journal_slug, f.journal));

    const sorted = Array.from(counts.entries()).sort((a, b) => b[1] - a[1]);
    els.journalFilter.innerHTML = `<option value="all">${t("allJournals")} (${ALL_FIGURES.length})</option>`;
    sorted.forEach(([slug, cnt]) => {
      const opt = document.createElement("option");
      opt.value = slug;
      opt.textContent = `${names.get(slug)} (${cnt})`;
      els.journalFilter.appendChild(opt);
    });
    els.journalFilter.value = state.journal;
  }

  function renderChipGroup(container, options, currentVal, onSelect) {
    container.innerHTML = "";
    options.forEach((opt) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "chip" + (String(currentVal) === String(opt.value) ? " active" : "");
      btn.setAttribute("data-value", opt.value);
      btn.innerHTML = opt.count != null
        ? `<span>${opt.label}</span><span class="chip-cnt">${opt.count}</span>`
        : `<span>${opt.label}</span>`;
      btn.addEventListener("click", () => onSelect(opt.value));
      container.appendChild(btn);
    });
  }

  function renderAllFilterChips() {
    const countBy = (key) => {
      const m = {};
      ALL_FIGURES.forEach((f) => {
        const k = String(f[key]);
        m[k] = (m[k] || 0) + 1;
      });
      return m;
    };
    const famC = countBy("family");
    const tierC = countBy("tier");
    const yrC = countBy("year");
    const discC = countBy("discipline");
    const patC = countBy("pattern");

    renderChipGroup(
      els.familyChips,
      [
        { value: "all", label: t("all"), count: ALL_FIGURES.length },
        { value: "cell", label: t("family.cell"), count: famC.cell || 0 },
        { value: "nature", label: t("family.nature"), count: famC.nature || 0 },
        { value: "science", label: t("family.science"), count: famC.science || 0 },
      ],
      state.family,
      (v) => { state.family = v; applyFilters(); }
    );

    renderChipGroup(
      els.tierChips,
      [
        { value: "all", label: t("all") },
        { value: "flagship", label: t("tier.flagship"), count: tierC.flagship || 0 },
        { value: "subjournal", label: t("tier.subjournal"), count: tierC.subjournal || 0 },
        { value: "oa-series", label: t("tier.oa-series"), count: tierC["oa-series"] || 0 },
      ],
      state.tier,
      (v) => { state.tier = v; applyFilters(); }
    );

    const years = (META.years && META.years.length ? META.years : [2026, 2025, 2024]).map(String);
    renderChipGroup(
      els.yearChips,
      [{ value: "all", label: t("all") }].concat(
        years.map((y) => ({ value: y, label: y, count: yrC[y] || 0 }))
      ),
      state.year,
      (v) => { state.year = v; applyFilters(); }
    );

    const discs = ["bio-med", "phys-eng", "energy-env", "mat-chem", "ai-comp", "inter-soc"];
    renderChipGroup(
      els.disciplineChips,
      [{ value: "all", label: t("all") }].concat(
        discs.map((d) => ({ value: d, label: t(`disc.${d}`), count: discC[d] || 0 }))
      ),
      state.discipline,
      (v) => { state.discipline = v; applyFilters(); }
    );

    const pats = ["graphical-abstract", "mechanism", "pipeline", "multipanel", "characterization"];
    renderChipGroup(
      els.patternChips,
      [{ value: "all", label: t("all") }].concat(
        pats.map((p) => ({ value: p, label: t(`pat.${p}`), count: patC[p] || 0 }))
      ),
      state.pattern,
      (v) => { state.pattern = v; applyFilters(); }
    );
  }

  function renderActiveFilterTags() {
    if (!els.activeFilterTags) return;
    els.activeFilterTags.innerHTML = "";
    const active = [];
    if (state.family !== "all") active.push({ label: t(`family.${state.family}`), clear: () => { state.family = "all"; } });
    if (state.tier !== "all") active.push({ label: t(`tier.${state.tier}`), clear: () => { state.tier = "all"; } });
    if (state.year !== "all") active.push({ label: state.year, clear: () => { state.year = "all"; } });
    if (state.discipline !== "all") active.push({ label: t(`disc.${state.discipline}`), clear: () => { state.discipline = "all"; } });
    if (state.pattern !== "all") active.push({ label: t(`pat.${state.pattern}`), clear: () => { state.pattern = "all"; } });
    if (state.journal !== "all") {
      const opt = els.journalFilter.options[els.journalFilter.selectedIndex];
      const lbl = opt ? opt.textContent.replace(/\s*\(\d+\)$/, "") : state.journal;
      active.push({ label: lbl, clear: () => { state.journal = "all"; els.journalFilter.value = "all"; } });
    }
    if (state.q.trim()) {
      active.push({ label: `"${state.q.trim()}"`, clear: () => { state.q = ""; els.search.value = ""; } });
    }

    active.forEach((item) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "active-tag";
      btn.innerHTML = `<span>${escapeHtml(item.label)}</span><span aria-hidden="true">×</span>`;
      btn.addEventListener("click", () => {
        item.clear();
        applyFilters();
      });
      els.activeFilterTags.appendChild(btn);
    });
  }

  function applyFilters() {
    const q = state.q.trim().toLowerCase();
    const tierOrder = { flagship: 0, subjournal: 1, "oa-series": 2 };

    let list = ALL_FIGURES.filter((f) => {
      if (state.family !== "all" && f.family !== state.family) return false;
      if (state.tier !== "all" && f.tier !== state.tier) return false;
      if (state.year !== "all" && String(f.year) !== String(state.year)) return false;
      if (state.discipline !== "all" && f.discipline !== state.discipline) return false;
      if (state.pattern !== "all" && f.pattern !== state.pattern) return false;
      if (state.journal !== "all" && f.journal_slug !== state.journal) return false;
      if (q) {
        const hay = `${f.title} ${f.journal} ${f.caption} ${f.doi} ${f.pmcid} ${(f.authors || []).join(" ")}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });

    list.sort((a, b) => {
      if (state.sort === "tier") {
        return (tierOrder[a.tier] - tierOrder[b.tier]) || (b.year - a.year) || (b.citations - a.citations);
      }
      if (state.sort === "citations") {
        return (b.citations - a.citations) || (b.year - a.year);
      }
      if (state.sort === "title") {
        return a.title.localeCompare(b.title);
      }
      return (b.year - a.year) || (tierOrder[a.tier] - tierOrder[b.tier]) || (b.citations - a.citations);
    });

    state.filtered = list;
    state.renderedCount = 0;

    const hasActive =
      state.family !== "all" ||
      state.tier !== "all" ||
      state.year !== "all" ||
      state.discipline !== "all" ||
      state.pattern !== "all" ||
      state.journal !== "all" ||
      Boolean(q);

    els.resetTop.hidden = !hasActive;
    els.clearSearch.hidden = !state.q;
    els.resultCount.textContent = t("showing")
      .replace("{n}", list.length.toLocaleString())
      .replace("{total}", ALL_FIGURES.length.toLocaleString());

    renderAllFilterChips();
    renderActiveFilterTags();
    syncQuickPillsAndTopics();
    syncQueryParams();

    if (window.scrollY > 360) {
      window.scrollTo({ top: 0, behavior: "auto" });
    }

    resetGalleryContainer();
    els.empty.hidden = list.length > 0;
    els.endHint.hidden = true;
    renderNextBatch();
  }

  function createCard(fig, idx) {
    const card = document.createElement("article");
    card.className = "fig-card";

    const w = fig.w > 0 ? fig.w : 1200;
    const h = fig.h > 0 ? fig.h : 800;
    const flagshipPill =
      fig.tier === "flagship"
        ? `<span class="tier-star-pill" title="Flagship">★ Flagship</span>`
        : "";

    const firstAuthor = (fig.authors && fig.authors[0]) ? fig.authors[0] : "";
    const bylineParts = [];
    if (firstAuthor) bylineParts.push(fig.authors.length > 1 ? `${firstAuthor} et al.` : firstAuthor);
    if (fig.doi) bylineParts.push(fig.doi);
    const byline = bylineParts.join(" · ");

    const dimsText = `${w}×${h}` + (fig.citations > 0 ? ` · Cited ${fig.citations}` : "");

    const curated = isCurated(fig);
    if (curated) card.setAttribute("data-curated", "1");

    const swatches = curated
      ? getCuratedSwatches(fig, false)
      : (fig.palette || []).map((hex) => ({ hex, roleLabel: "" }));
    const swatchesHtml = swatches
      .map((sw) => {
        const tip = sw.roleLabel ? `${sw.roleLabel} · ${sw.hex}` : sw.hex;
        return `<button class="swatch-segment" type="button" style="background:${sw.hex}" title="${escapeHtml(tip)}" data-hex="${sw.hex}" aria-label="Copy ${sw.hex}"></button>`;
      })
      .join("");

    const paletteHtml = curated
      ? `
      <div class="card-palette is-curated">
        <div class="curated-meta-row">
          <span class="curated-badge">${escapeHtml(t("curated.badge"))}</span>
          <a class="agent-json-link" href="${getAgentItemUrl(fig)}" target="_blank" rel="noopener noreferrer">${escapeHtml(t("curated.agentJson"))}</a>
        </div>
        <div class="card-palette-row">
          <div class="swatch-bar">${swatchesHtml}</div>
          <button class="card-py-btn" type="button" title="Copy Python palette">Py</button>
        </div>
      </div>`
      : `
      <div class="card-palette">
        <div class="swatch-bar">${swatchesHtml}</div>
        <button class="card-py-btn" type="button" title="Copy Python palette">Py</button>
      </div>`;

    card.innerHTML = `
      <div class="card-header-bar">
        <span class="card-journal-pill" title="${escapeHtml(fig.journal)}">
          <span class="journal-bar bar-${fig.family}"></span>
          <span class="card-journal-name">${escapeHtml(fig.journal_short || fig.journal)}</span>
          <span class="card-year">${fig.year}</span>
        </span>
        <span class="card-header-right">
          ${flagshipPill}
          <span class="fig-lbl-pill">${escapeHtml(fig.figure_label || "Fig. 1")}</span>
        </span>
      </div>
      <div class="fig-thumb-wrap" data-idx="${idx}">
        <img src="${fig.image}" alt="${escapeHtml(fig.title)}" loading="lazy" decoding="async" referrerpolicy="no-referrer" width="${w}" height="${h}" style="aspect-ratio: ${w} / ${h};">
        <span class="thumb-dims-pill">${escapeHtml(dimsText)}</span>
      </div>
      <div class="fig-body">
        <h3 class="fig-title" data-idx="${idx}" title="${escapeHtml(fig.title)}">${escapeHtml(fig.title)}</h3>
        ${byline ? `<div class="fig-byline" title="${escapeHtml(byline)}">${escapeHtml(byline)}</div>` : ""}
        <div class="fig-tags">
          <button type="button" class="mini-tag" data-filter-disc="${fig.discipline}">${t("disc." + fig.discipline)}</button>
          <button type="button" class="mini-tag" data-filter-pat="${fig.pattern}">${t("pat." + fig.pattern)}</button>
        </div>
      </div>
      ${paletteHtml}
    `;

    const imgEl = card.querySelector("img");
    imgEl.addEventListener("error", () => {
      if (imgEl.dataset.fallbackDone) return;
      imgEl.dataset.fallbackDone = "1";
      const fb = document.createElement("div");
      fb.className = "fig-img-fallback";
      fb.textContent = `${fig.journal} · ${fig.figure_label || "Figure 1"}`;
      imgEl.replaceWith(fb);
    });

    card.querySelector(".fig-thumb-wrap").addEventListener("click", () => openLightbox(idx));
    card.querySelector(".fig-title").addEventListener("click", () => openLightbox(idx));

    const discBtn = card.querySelector("[data-filter-disc]");
    if (discBtn) {
      discBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        state.discipline = fig.discipline;
        applyFilters();
      });
    }
    const patBtn = card.querySelector("[data-filter-pat]");
    if (patBtn) {
      patBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        state.pattern = fig.pattern;
        applyFilters();
      });
    }

    const agentLink = card.querySelector(".agent-json-link");
    if (agentLink) {
      agentLink.addEventListener("click", (e) => e.stopPropagation());
    }

    card.querySelectorAll(".swatch-segment").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const hex = btn.getAttribute("data-hex");
        copyText(hex, hex);
      });
    });

    const pyBtn = card.querySelector(".card-py-btn");
    if (pyBtn) {
      pyBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        copyText(`palette = ${JSON.stringify(getEffectivePaletteHexes(fig))}`, "Python palette");
      });
    }

    return card;
  }

  function checkSentinelVisible() {
    if (state.renderedCount >= state.filtered.length || els.sentinel.hidden) return;
    const rect = els.sentinel.getBoundingClientRect();
    if (rect.top <= window.innerHeight + 420) {
      renderNextBatch();
    }
  }

  function scheduleScrollCheck() {
    if (scrollCheckScheduled) return;
    scrollCheckScheduled = true;
    requestAnimationFrame(() => {
      scrollCheckScheduled = false;
      checkSentinelVisible();
    });
  }

  function renderNextBatch() {
    if (state.renderedCount >= state.filtered.length) {
      els.sentinel.hidden = true;
      if (state.filtered.length > 0) {
        els.endHint.hidden = false;
        els.endHint.textContent = t("endHint").replace("{n}", state.filtered.length.toLocaleString());
      }
      return;
    }

    const end = Math.min(state.renderedCount + PAGE_SIZE, state.filtered.length);
    if (state.layout === "masonry") {
      if (!masonryCols.length) resetGalleryContainer();
      const frags = masonryCols.map(() => document.createDocumentFragment());
      for (let i = state.renderedCount; i < end; i++) {
        const fig = state.filtered[i];
        let minCol = 0;
        for (let c = 1; c < masonryHeights.length; c++) {
          if (masonryHeights[c] < masonryHeights[minCol]) minCol = c;
        }
        frags[minCol].appendChild(createCard(fig, i));
        const ratio = fig.w > 0 && fig.h > 0 ? Math.min(fig.h / fig.w, 1.5) : 0.7;
        masonryHeights[minCol] += ratio + 0.52;
      }
      frags.forEach((f, c) => masonryCols[c].appendChild(f));
    } else {
      const frag = document.createDocumentFragment();
      for (let i = state.renderedCount; i < end; i++) {
        frag.appendChild(createCard(state.filtered[i], i));
      }
      els.gallery.appendChild(frag);
    }

    state.renderedCount = end;

    const more = state.renderedCount < state.filtered.length;
    els.sentinel.hidden = !more;
    if (!more && state.filtered.length > 0) {
      els.endHint.hidden = false;
      els.endHint.textContent = t("endHint").replace("{n}", state.filtered.length.toLocaleString());
    } else if (more) {
      scheduleScrollCheck();
    }
  }

  function setLayoutMode(mode) {
    if (!LAYOUT_MODES.includes(mode)) return;
    state.layout = mode;
    localStorage.setItem("cns_layout", state.layout);
    applyLayout();
    const prevCount = state.renderedCount || PAGE_SIZE;
    state.renderedCount = 0;
    resetGalleryContainer();
    const target = Math.min(prevCount, state.filtered.length);
    while (state.renderedCount < target) {
      renderNextBatch();
    }
  }

  function openLightbox(idx) {
    if (idx < 0 || idx >= state.filtered.length) return;
    state.lbIndex = idx;
    const fig = state.filtered[idx];

    els.lbImgWrap.classList.remove("zoomed");
    els.lbImg.referrerPolicy = "no-referrer";
    els.lbImg.src = fig.image;
    els.lbImg.alt = fig.title;
    if (fig.highres && fig.highres !== fig.image) {
      const hi = new Image();
      hi.referrerPolicy = "no-referrer";
      hi.onload = () => {
        if (state.lbIndex === idx) els.lbImg.src = fig.highres;
      };
      hi.onerror = () => {};
      hi.src = fig.highres;
    }

    els.lbFamily.className = `badge family-${fig.family}`;
    els.lbFamily.textContent = t(`family.${fig.family}`);
    els.lbTier.textContent = t(`tier.${fig.tier}`);
    els.lbYear.textContent = fig.year;
    els.lbDiscipline.textContent = t(`disc.${fig.discipline}`);
    els.lbPattern.textContent = t(`pat.${fig.pattern}`);
    els.lbLicense.textContent = fig.license || "OA";

    els.lbTitle.textContent = fig.title;
    els.lbJournalMeta.textContent = `${fig.journal} · ${fig.pub_date || fig.year} · Citations: ${fig.citations || 0} · ${fig.doi}`;
    els.lbAuthors.textContent = (fig.authors || []).join(", ");
    els.lbFigLabel.textContent = fig.figure_label || "Fig. 1";
    els.lbDims.textContent = `${fig.w} × ${fig.h} px`;
    els.lbCaption.textContent = fig.caption || "(No caption text available)";

    const curated = isCurated(fig);
    if (els.lbPaletteTitle) {
      els.lbPaletteTitle.textContent = curated ? t("curated.lbTitle") : t("lb.paletteTitle");
    }
    els.lbPalette.innerHTML = "";
    els.lbPalette.classList.toggle("is-curated", curated);
    if (curated) {
      getCuratedSwatches(fig, true).forEach((sw) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "lb-swatch";
        btn.innerHTML = `<span class="lb-swatch-color" style="background:${sw.hex}"></span><span class="lb-swatch-hex">${sw.hex}</span><span class="lb-swatch-role">${escapeHtml(sw.roleLabel)}</span>`;
        btn.addEventListener("click", () => copyText(sw.hex, sw.hex));
        els.lbPalette.appendChild(btn);
      });
      if (els.lbLayoutNotes) {
        const cbBadge = fig.palette_curated.colorblind_safe
          ? `<span class="cb-safe-pill">✓ ${escapeHtml(t("curated.cbSafe"))}</span>`
          : "";
        els.lbLayoutNotes.innerHTML = `
          <div class="lb-layout-head">
            <strong>${escapeHtml(t("curated.layoutLabel"))}</strong>
            ${cbBadge}
          </div>
          <p class="lb-layout-text">${escapeHtml(fig.palette_curated.layout_notes || "")}</p>
        `;
        els.lbLayoutNotes.hidden = false;
      }
      if (els.lbAgentJson) {
        els.lbAgentJson.hidden = false;
        els.lbAgentJson.href = getAgentItemUrl(fig);
      }
    } else {
      (fig.palette || []).forEach((hex) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "lb-swatch";
        btn.innerHTML = `<span class="lb-swatch-color" style="background:${hex}"></span><span class="lb-swatch-hex">${hex}</span>`;
        btn.addEventListener("click", () => copyText(hex, hex));
        els.lbPalette.appendChild(btn);
      });
      if (els.lbLayoutNotes) {
        els.lbLayoutNotes.hidden = true;
        els.lbLayoutNotes.innerHTML = "";
      }
      if (els.lbAgentJson) {
        els.lbAgentJson.hidden = true;
        els.lbAgentJson.removeAttribute("href");
      }
    }

    els.lbViewImage.href = fig.highres || fig.image;
    els.lbOpenPaper.href = fig.paper;
    if (fig.pmcid) {
      els.lbOpenPmc.hidden = false;
      els.lbOpenPmc.href = fig.pmc_url || `https://pmc.ncbi.nlm.nih.gov/articles/${fig.pmcid}/`;
    } else {
      els.lbOpenPmc.hidden = true;
    }

    els.lb.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function closeLightbox() {
    els.lb.hidden = true;
    state.lbIndex = -1;
    document.body.style.overflow = "";
    if (window.location.hash && window.location.hash.startsWith("#fig=")) {
      window.history.replaceState(null, "", window.location.pathname + window.location.search);
    }
  }

  function openDeepLinkedFigure() {
    const targetId = getDeepLinkFigureId();
    if (!targetId) return;
    let idx = state.filtered.findIndex((f) => f.id === targetId);
    if (idx < 0 && ALL_FIGURES.some((f) => f.id === targetId)) {
      resetAll();
      idx = state.filtered.findIndex((f) => f.id === targetId);
    }
    if (idx >= 0) {
      openLightbox(idx);
    }
  }

  function openPaletteStudio() {
    const items = state.filtered.slice(0, 36);
    els.pmGrid.innerHTML = "";
    items.forEach((fig) => {
      const card = document.createElement("div");
      card.className = "pm-card";
      const pal = getEffectivePaletteHexes(fig);
      const curatedTag = isCurated(fig)
        ? `<span class="pm-curated-tag">${escapeHtml(t("curated.badge"))}</span>`
        : "";
      const bar = pal
        .map((hex) => `<span style="background:${hex}" title="${hex}" data-hex="${hex}"></span>`)
        .join("");
      card.innerHTML = `
        <div class="pm-card-title">${escapeHtml(fig.journal_short || fig.journal)} · ${fig.year}${curatedTag}</div>
        <div class="pm-card-sub">${escapeHtml(fig.title.slice(0, 66))}${fig.title.length > 66 ? "…" : ""}</div>
        <div class="pm-bar">${bar}</div>
        <div style="display:flex;gap:6px;justify-content:space-between;align-items:center;">
          <span style="font-family:var(--font-mono);font-size:0.72rem;color:var(--soft)">${pal.join(" ")}</span>
          <button class="mini-btn pm-copy-py" type="button">Copy Py</button>
        </div>
      `;
      card.querySelectorAll(".pm-bar span").forEach((s) => {
        s.addEventListener("click", () => copyText(s.getAttribute("data-hex"), s.getAttribute("data-hex")));
      });
      card.querySelector(".pm-copy-py").addEventListener("click", () => {
        copyText(`palette = ${JSON.stringify(pal)}`, "Python palette");
      });
      els.pmGrid.appendChild(card);
    });
    els.pm.hidden = false;
  }

  function resetAll() {
    state.family = "all";
    state.tier = "all";
    state.year = "all";
    state.discipline = "all";
    state.pattern = "all";
    state.journal = "all";
    state.q = "";
    els.search.value = "";
    els.journalFilter.value = "all";
    applyFilters();
  }

  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // Event wiring
  els.quickStatPills.forEach((btn) => {
    btn.addEventListener("click", () => {
      const qFam = btn.getAttribute("data-quick-family");
      const qTier = btn.getAttribute("data-quick-tier");
      if (qFam === "all") {
        state.family = "all";
        state.tier = "all";
      } else if (qFam) {
        state.family = state.family === qFam ? "all" : qFam;
      } else if (qTier) {
        state.tier = state.tier === qTier ? "all" : qTier;
      }
      applyFilters();
    });
  });

  els.topicChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const topic = chip.getAttribute("data-topic") || "";
      if (state.q.trim().toLowerCase() === topic.toLowerCase()) {
        state.q = "";
      } else {
        state.q = topic;
      }
      els.search.value = state.q;
      applyFilters();
    });
  });

  if (els.toggleFiltersBtn) {
    els.toggleFiltersBtn.addEventListener("click", () => {
      state.filtersCollapsed = !state.filtersCollapsed;
      localStorage.setItem("cns_filters_collapsed", state.filtersCollapsed ? "1" : "0");
      applyFiltersCollapseState();
    });
  }

  els.search.addEventListener("input", () => {
    state.q = els.search.value;
    applyFilters();
  });
  els.clearSearch.addEventListener("click", () => {
    state.q = "";
    els.search.value = "";
    applyFilters();
  });
  els.sort.addEventListener("change", () => {
    state.sort = els.sort.value;
    applyFilters();
  });
  els.journalFilter.addEventListener("change", () => {
    state.journal = els.journalFilter.value;
    applyFilters();
  });

  if (els.viewSwitch) {
    els.viewSwitch.querySelectorAll(".view-tab").forEach((btn) => {
      btn.addEventListener("click", () => setLayoutMode(btn.getAttribute("data-layout")));
    });
  }
  els.densityToggle.addEventListener("click", () => {
    const idx = LAYOUT_MODES.indexOf(state.layout);
    setLayoutMode(LAYOUT_MODES[(idx + 1) % LAYOUT_MODES.length]);
  });

  els.langToggle.addEventListener("click", () => {
    state.lang = state.lang === "zh" ? "en" : "zh";
    localStorage.setItem("cns_lang", state.lang);
    applyTranslations();
    buildJournalDropdown();
    applyFilters();
  });
  els.themeToggle.addEventListener("click", () => {
    state.theme = state.theme === "dark" ? "light" : "dark";
    localStorage.setItem("cns_theme", state.theme);
    applyTheme();
  });

  els.resetTop.addEventListener("click", resetAll);
  els.resetAll.addEventListener("click", resetAll);

  els.lbClose.addEventListener("click", closeLightbox);
  els.lbBackdrop.addEventListener("click", closeLightbox);
  els.lbPrev.addEventListener("click", () => {
    if (state.lbIndex > 0) openLightbox(state.lbIndex - 1);
  });
  els.lbNext.addEventListener("click", () => {
    if (state.lbIndex + 1 < state.filtered.length) openLightbox(state.lbIndex + 1);
  });
  els.lbZoom.addEventListener("click", () => els.lbImgWrap.classList.toggle("zoomed"));
  els.lbImg.addEventListener("click", () => els.lbImgWrap.classList.toggle("zoomed"));

  els.lbCopyPy.addEventListener("click", () => {
    const fig = state.filtered[state.lbIndex];
    if (fig) copyText(`palette = ${JSON.stringify(getEffectivePaletteHexes(fig))}`, "Python list");
  });
  els.lbCopyR.addEventListener("click", () => {
    const fig = state.filtered[state.lbIndex];
    if (fig) {
      const pal = getEffectivePaletteHexes(fig);
      copyText(`palette <- c(${pal.map((c) => `"${c}"`).join(", ")})`, "R vector");
    }
  });
  els.lbCopyCss.addEventListener("click", () => {
    const fig = state.filtered[state.lbIndex];
    if (fig) {
      const pal = getEffectivePaletteHexes(fig);
      const css = pal.map((c, i) => `--cns-color-${i + 1}: ${c};`).join("\n");
      copyText(css, "CSS variables");
    }
  });
  els.lbCopyBib.addEventListener("click", () => {
    const fig = state.filtered[state.lbIndex];
    if (!fig) return;
    const firstAuthor = (fig.authors && fig.authors[0] ? fig.authors[0].split(" ").slice(-1)[0] : "Author").replace(/[^a-zA-Z0-9]/g, "");
    const keySuffix = (fig.pmcid || fig.doi || "item").replace(/[^a-zA-Z0-9]/g, "").slice(-10);
    const bib = `@article{${firstAuthor}${fig.year}_${keySuffix},\n  title={${fig.title}},\n  author={${(fig.authors || []).join(" and ")}},\n  journal={${fig.journal}},\n  year={${fig.year}},\n  doi={${fig.doi}}\n}`;
    copyText(bib, "BibTeX");
  });

  els.paletteStudioBtn.addEventListener("click", openPaletteStudio);
  els.pmClose.addEventListener("click", () => (els.pm.hidden = true));
  els.pmBackdrop.addEventListener("click", () => (els.pm.hidden = true));
  if (els.supportBtn && els.sm) {
    els.supportBtn.addEventListener("click", () => (els.sm.hidden = false));
    if (els.smClose) els.smClose.addEventListener("click", () => (els.sm.hidden = true));
    if (els.smBackdrop) els.smBackdrop.addEventListener("click", () => (els.sm.hidden = true));
  }

  document.addEventListener("keydown", (e) => {
    if (!els.lb.hidden) {
      if (e.key === "Escape") closeLightbox();
      else if (e.key === "ArrowLeft" && state.lbIndex > 0) openLightbox(state.lbIndex - 1);
      else if (e.key === "ArrowRight" && state.lbIndex + 1 < state.filtered.length) openLightbox(state.lbIndex + 1);
    } else if (!els.pm.hidden && e.key === "Escape") {
      els.pm.hidden = true;
    } else if (els.sm && !els.sm.hidden && e.key === "Escape") {
      els.sm.hidden = true;
    } else if (
      e.key === "/" &&
      document.activeElement !== els.search &&
      !["INPUT", "TEXTAREA", "SELECT"].includes((document.activeElement && document.activeElement.tagName) || "")
    ) {
      e.preventDefault();
      els.search.focus();
    }
  });

  const io = new IntersectionObserver(
    (entries) => {
      if (entries.some((en) => en.isIntersecting)) renderNextBatch();
    },
    { rootMargin: "420px" }
  );
  io.observe(els.sentinel);
  els.sentinel.addEventListener("click", renderNextBatch);
  window.addEventListener("scroll", scheduleScrollCheck, { passive: true });
  window.addEventListener(
    "resize",
    () => {
      if (state.layout === "masonry" && getMasonryColumnCount() !== currentColCount) {
        const prevCount = state.renderedCount || PAGE_SIZE;
        state.renderedCount = 0;
        resetGalleryContainer();
        const target = Math.min(prevCount, state.filtered.length);
        while (state.renderedCount < target) {
          renderNextBatch();
        }
      }
      scheduleScrollCheck();
    },
    { passive: true }
  );

  // Init
  applyTheme();
  readQueryParams();
  applyTranslations();
  updateHeroStats();
  buildJournalDropdown();
  applyFilters();
  openDeepLinkedFigure();
  window.addEventListener("hashchange", openDeepLinkedFigure);
})();
