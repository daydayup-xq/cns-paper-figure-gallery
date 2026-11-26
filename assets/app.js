(function () {
  "use strict";

  const ALL_FIGURES = Array.isArray(window.FIGURES) ? window.FIGURES : [];
  const META = window.GALLERY_META || {};
  const PAGE_SIZE = 32;

  const state = {
    lang: localStorage.getItem("ncs_lang") || "zh",
    theme: localStorage.getItem("ncs_theme") || "light",
    layout: localStorage.getItem("ncs_layout") || "masonry",
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
    sort: document.getElementById("sort"),
    journalFilter: document.getElementById("journal-filter"),
    densityToggle: document.getElementById("density-toggle"),
    densityLabel: document.getElementById("density-label"),
    resetTop: document.getElementById("reset-top"),
    resetAll: document.getElementById("reset-all"),
    familyChips: document.getElementById("family-chips"),
    tierChips: document.getElementById("tier-chips"),
    yearChips: document.getElementById("year-chips"),
    disciplineChips: document.getElementById("discipline-chips"),
    patternChips: document.getElementById("pattern-chips"),
    langToggle: document.getElementById("lang-toggle"),
    themeToggle: document.getElementById("theme-toggle"),
    paletteStudioBtn: document.getElementById("palette-studio-btn"),
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
    lbPalette: document.getElementById("lb-palette"),
    lbCopyPy: document.getElementById("lb-copy-py"),
    lbCopyR: document.getElementById("lb-copy-r"),
    lbCopyCss: document.getElementById("lb-copy-css"),
    lbViewImage: document.getElementById("lb-view-image"),
    lbOpenPaper: document.getElementById("lb-open-paper"),
    lbOpenPmc: document.getElementById("lb-open-pmc"),
    lbCopyBib: document.getElementById("lb-copy-bib"),
    pm: document.getElementById("palette-modal"),
    pmBackdrop: document.getElementById("pm-backdrop"),
    pmClose: document.getElementById("pm-close"),
    pmGrid: document.getElementById("pm-grid"),
  };

  function t(key) {
    const dict = (window.I18N && window.I18N[state.lang]) || {};
    return dict[key] || key;
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
    els.gallery.className = state.layout === "grid" ? "grid-view" : "masonry";
    els.densityLabel.textContent = state.layout === "grid" ? t("layout.grid") : t("layout.masonry");
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
    if (state.sort !== "year") p.set("sort", state.sort);
    const qs = p.toString();
    const nextUrl = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
    window.history.replaceState(null, "", nextUrl);
  }

  function updateHeroStats() {
    const nat = ALL_FIGURES.filter((f) => f.family === "nature").length;
    const sci = ALL_FIGURES.filter((f) => f.family === "science").length;
    const cell = ALL_FIGURES.filter((f) => f.family === "cell").length;
    const flag = ALL_FIGURES.filter((f) => f.tier === "flagship").length;
    document.getElementById("stat-total").textContent = ALL_FIGURES.length;
    document.getElementById("stat-nature").textContent = nat;
    document.getElementById("stat-science").textContent = sci;
    document.getElementById("stat-cell").textContent = cell;
    document.getElementById("stat-flagship").textContent = flag;
    if (META.updated_at) {
      els.footerUpdated.textContent = META.updated_at.replace("T", " ").replace("Z", " UTC");
    }
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
        { value: "nature", label: t("family.nature"), count: famC.nature || 0 },
        { value: "science", label: t("family.science"), count: famC.science || 0 },
        { value: "cell", label: t("family.cell"), count: famC.cell || 0 },
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

    const discs = ["bio-med", "mat-chem", "energy-env", "phys-eng", "ai-comp", "inter-soc"];
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
      .replace("{n}", list.length)
      .replace("{total}", ALL_FIGURES.length);

    renderAllFilterChips();
    syncQueryParams();

    els.gallery.innerHTML = "";
    els.empty.hidden = list.length > 0;
    els.endHint.hidden = true;
    renderNextBatch();
  }

  function createCard(fig, idx) {
    const card = document.createElement("article");
    card.className = "fig-card";

    const famClass = `pill-${fig.family}`;
    const flagshipBadge =
      fig.tier === "flagship"
        ? `<span class="pill-badge pill-flagship">★ Flagship</span>`
        : "";

    const swatchesHtml = (fig.palette || [])
      .map(
        (hex) =>
          `<button class="swatch-dot" type="button" style="background:${hex}" title="${hex}" data-hex="${hex}" aria-label="Copy ${hex}"></button>`
      )
      .join("");

    card.innerHTML = `
      <div class="fig-thumb-wrap" data-idx="${idx}">
        <img src="${fig.image}" alt="${escapeHtml(fig.title)}" loading="lazy" decoding="async" width="${fig.w}" height="${fig.h}">
        <div class="fig-top-badges">
          <span class="pill-badge ${famClass}">${escapeHtml(fig.journal_short || fig.journal)} · ${fig.year}</span>
          ${flagshipBadge}
        </div>
      </div>
      <div class="fig-body">
        <div class="fig-meta-line">
          <span class="fig-journal" title="${escapeHtml(fig.journal)}">${escapeHtml(fig.journal)}</span>
          <span>${escapeHtml(fig.figure_label)}</span>
        </div>
        <h3 class="fig-title" data-idx="${idx}" title="${escapeHtml(fig.title)}">${escapeHtml(fig.title)}</h3>
        <div class="fig-tags">
          <span class="mini-tag">${t("disc." + fig.discipline)}</span>
          <span class="mini-tag">${t("pat." + fig.pattern)}</span>
        </div>
      </div>
      <div class="card-palette">
        <span class="palette-label">PALETTE</span>
        ${swatchesHtml}
      </div>
    `;

    card.querySelector(".fig-thumb-wrap").addEventListener("click", () => openLightbox(idx));
    card.querySelector(".fig-title").addEventListener("click", () => openLightbox(idx));
    card.querySelectorAll(".swatch-dot").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const hex = btn.getAttribute("data-hex");
        copyText(hex, hex);
      });
    });

    return card;
  }

  function renderNextBatch() {
    if (state.renderedCount >= state.filtered.length) {
      els.sentinel.hidden = true;
      if (state.filtered.length > 0) {
        els.endHint.hidden = false;
        els.endHint.textContent = t("endHint").replace("{n}", state.filtered.length);
      }
      return;
    }
    const end = Math.min(state.renderedCount + PAGE_SIZE, state.filtered.length);
    const frag = document.createDocumentFragment();
    for (let i = state.renderedCount; i < end; i++) {
      frag.appendChild(createCard(state.filtered[i], i));
    }
    els.gallery.appendChild(frag);
    state.renderedCount = end;

    const more = state.renderedCount < state.filtered.length;
    els.sentinel.hidden = !more;
    if (!more && state.filtered.length > 0) {
      els.endHint.hidden = false;
      els.endHint.textContent = t("endHint").replace("{n}", state.filtered.length);
    }
  }

  function openLightbox(idx) {
    if (idx < 0 || idx >= state.filtered.length) return;
    state.lbIndex = idx;
    const fig = state.filtered[idx];

    els.lbImgWrap.classList.remove("zoomed");
    els.lbImg.src = fig.image;
    els.lbImg.alt = fig.title;
    if (fig.highres && fig.highres !== fig.image) {
      const hi = new Image();
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

    els.lbPalette.innerHTML = "";
    (fig.palette || []).forEach((hex) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "lb-swatch";
      btn.innerHTML = `<span class="lb-swatch-color" style="background:${hex}"></span><span class="lb-swatch-hex">${hex}</span>`;
      btn.addEventListener("click", () => copyText(hex, hex));
      els.lbPalette.appendChild(btn);
    });

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
  }

  function openPaletteStudio() {
    const items = state.filtered.slice(0, 36);
    els.pmGrid.innerHTML = "";
    items.forEach((fig) => {
      const card = document.createElement("div");
      card.className = "pm-card";
      const bar = (fig.palette || [])
        .map((hex) => `<span style="background:${hex}" title="${hex}" data-hex="${hex}"></span>`)
        .join("");
      card.innerHTML = `
        <div class="pm-card-title">${escapeHtml(fig.journal_short || fig.journal)} · ${fig.year}</div>
        <div class="pm-card-sub">${escapeHtml(fig.title.slice(0, 66))}${fig.title.length > 66 ? "…" : ""}</div>
        <div class="pm-bar">${bar}</div>
        <div style="display:flex;gap:6px;justify-content:space-between;align-items:center;">
          <span style="font-family:var(--font-mono);font-size:0.72rem;color:var(--soft)">${(fig.palette || []).join(" ")}</span>
          <button class="mini-btn pm-copy-py" type="button">Copy Py</button>
        </div>
      `;
      card.querySelectorAll(".pm-bar span").forEach((s) => {
        s.addEventListener("click", () => copyText(s.getAttribute("data-hex"), s.getAttribute("data-hex")));
      });
      card.querySelector(".pm-copy-py").addEventListener("click", () => {
        copyText(`palette = ${JSON.stringify(fig.palette)}`, "Python palette");
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
  els.densityToggle.addEventListener("click", () => {
    state.layout = state.layout === "masonry" ? "grid" : "masonry";
    localStorage.setItem("ncs_layout", state.layout);
    applyLayout();
  });
  els.langToggle.addEventListener("click", () => {
    state.lang = state.lang === "zh" ? "en" : "zh";
    localStorage.setItem("ncs_lang", state.lang);
    applyTranslations();
    buildJournalDropdown();
    applyFilters();
  });
  els.themeToggle.addEventListener("click", () => {
    state.theme = state.theme === "dark" ? "light" : "dark";
    localStorage.setItem("ncs_theme", state.theme);
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
    if (fig) copyText(`palette = ${JSON.stringify(fig.palette)}`, "Python list");
  });
  els.lbCopyR.addEventListener("click", () => {
    const fig = state.filtered[state.lbIndex];
    if (fig) copyText(`palette <- c(${fig.palette.map((c) => `"${c}"`).join(", ")})`, "R vector");
  });
  els.lbCopyCss.addEventListener("click", () => {
    const fig = state.filtered[state.lbIndex];
    if (fig) {
      const css = fig.palette.map((c, i) => `--ncs-color-${i + 1}: ${c};`).join("\n");
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

  document.addEventListener("keydown", (e) => {
    if (!els.lb.hidden) {
      if (e.key === "Escape") closeLightbox();
      else if (e.key === "ArrowLeft" && state.lbIndex > 0) openLightbox(state.lbIndex - 1);
      else if (e.key === "ArrowRight" && state.lbIndex + 1 < state.filtered.length) openLightbox(state.lbIndex + 1);
    } else if (!els.pm.hidden && e.key === "Escape") {
      els.pm.hidden = true;
    }
  });

  const io = new IntersectionObserver(
    (entries) => {
      if (entries.some((en) => en.isIntersecting)) renderNextBatch();
    },
    { rootMargin: "320px" }
  );
  io.observe(els.sentinel);

  // Init
  applyTheme();
  readQueryParams();
  applyTranslations();
  updateHeroStats();
  buildJournalDropdown();
  applyFilters();
})();
