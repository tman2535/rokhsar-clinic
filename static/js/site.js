/* Rokhsar clinic — public site behaviour (no dependencies).
 * Modules: theme · header · filters · before/after slider · Jalali date picker ·
 *          booking forms · page context · chat widget · procedure page helpers
 */
(function () {
  "use strict";

  const CFG = readJSON("rk-config") || {};
  const PAGE = readJSON("page-context") || {};
  const T = CFG.t || {};
  const LANG = CFG.lang || document.documentElement.lang || "fa";
  const RTL = (CFG.dir || document.dir) === "rtl";
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.documentElement.classList.add("js");

  /* ───────────── helpers ───────────── */
  function readJSON(id) {
    const el = document.getElementById(id);
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } },
    del(k) { try { localStorage.removeItem(k); } catch (e) { /* ignore */ } },
  };
  const FA = "۰۱۲۳۴۵۶۷۸۹", AR = "٠١٢٣٤٥٦٧٨٩";
  function digits(value) {
    const s = String(value);
    if (LANG === "fa") return s.replace(/\d/g, (d) => FA[d]);
    if (LANG === "ar") return s.replace(/\d/g, (d) => AR[d]);
    return s;
  }
  function cookie(name) {
    const m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[1]) : "";
  }
  function csrf() {
    const input = $("input[name=csrfmiddlewaretoken]");
    return cookie("csrftoken") || (input && input.value) || "";
  }
  async function api(url, opts) {
    opts = opts || {};
    const headers = Object.assign({ "X-Requested-With": "fetch", "Accept": "application/json" }, opts.headers || {});
    if (opts.method && opts.method !== "GET") headers["X-CSRFToken"] = csrf();
    let body = opts.body;
    if (opts.json) { headers["Content-Type"] = "application/json"; body = JSON.stringify(opts.json); }
    const res = await fetch(url, { method: opts.method || "GET", headers, body, credentials: "same-origin" });
    let data = {};
    try { data = await res.json(); } catch (e) { /* non-JSON */ }
    return { ok: res.ok && data.ok !== false, status: res.status, data };
  }
  const pad = (n) => String(n).padStart(2, "0");
  const iso = (y, m, d) => `${y}-${pad(m)}-${pad(d)}`;

  /* ───────────── theme ───────────── */
  $$("[data-theme-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      store.set("rk-theme", next);
    });
  });

  /* ───────────── header ───────────── */
  const header = $("[data-header]");
  if (header) {
    let lastY = window.scrollY;
    let ticking = false;
    window.addEventListener("scroll", () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const y = window.scrollY;
        const menuOpen = header.querySelector("[aria-expanded=true]");
        header.classList.toggle("is-scrolled", y > 8);
        header.classList.toggle("is-hidden", !menuOpen && y > 320 && y > lastY + 4);
        if (y < lastY - 4 || y < 320) header.classList.remove("is-hidden");
        lastY = y;
        ticking = false;
      });
    }, { passive: true });
  }

  function popover(toggle, panel, opts) {
    if (!toggle || !panel) return;
    const close = () => { toggle.setAttribute("aria-expanded", "false"); panel.hidden = true; };
    const open = () => { toggle.setAttribute("aria-expanded", "true"); panel.hidden = false; };
    toggle.addEventListener("click", (e) => {
      e.stopPropagation();
      toggle.getAttribute("aria-expanded") === "true" ? close() : open();
    });
    document.addEventListener("click", (e) => { if (!panel.contains(e.target) && e.target !== toggle) close(); });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") { close(); toggle.focus(); }
    });
    if (opts && opts.hover && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
      let timer;
      const wrap = toggle.parentElement;
      wrap.addEventListener("mouseenter", () => { clearTimeout(timer); open(); });
      wrap.addEventListener("mouseleave", () => { timer = setTimeout(close, 180); });
    }
    return { open, close };
  }
  popover($("[data-mega-toggle]"), $("#mega-menu"), { hover: true });
  popover($("[data-lang-toggle]"), $(".lang__menu"));
  popover($("[data-menu-toggle]"), $("#mobile-menu"));
  $$("#mobile-menu a[href*='#']").forEach((a) => a.addEventListener("click", () => {
    const t = $("[data-menu-toggle]"); t.setAttribute("aria-expanded", "false"); $("#mobile-menu").hidden = true;
  }));
  // Remember the language so a visit to "/" lands in the same language next time.
  $$("[data-set-lang]").forEach((a) => a.addEventListener("click", () => {
    document.cookie = `rk_lang=${a.dataset.setLang};path=/;max-age=31536000;samesite=lax`;
  }));

  /* ───────────── filter tabs ───────────── */
  $$("[data-filter-group]").forEach((group) => {
    const items = $(`[data-filter-items="${group.dataset.filterGroup}"]`);
    if (!items) return;
    const tabs = $$("[data-filter]", group);
    tabs.forEach((tab) => tab.addEventListener("click", () => {
      tabs.forEach((t) => t.setAttribute("aria-selected", String(t === tab)));
      const f = tab.dataset.filter;
      Array.from(items.children).forEach((el) => { el.hidden = f !== "all" && el.dataset.cat !== f; });
    }));
    group.addEventListener("keydown", (e) => {
      const i = tabs.indexOf(document.activeElement);
      if (i < 0) return;
      const step = { ArrowRight: RTL ? -1 : 1, ArrowLeft: RTL ? 1 : -1 }[e.key];
      if (!step) return;
      e.preventDefault();
      const next = tabs[(i + step + tabs.length) % tabs.length];
      next.focus(); next.click();
    });
  });

  /* ───────────── before / after slider ─────────────
   Mouse: the line follows the cursor with a soft spring and settles back to
   the middle when the cursor leaves. Touch/pen: drag. Keyboard: arrow keys. */
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  function initSlider(root) {
    const handle = $(".ba__handle", root);
    let pos = 50;          // shown position, physical % from the left edge
    let target = 50;       // where the spring is heading
    let dragging = false;
    let raf = null;
    let introAnim = null;

    // "After" share for screen readers: in RTL the after layer sits left of the line.
    const afterShare = () => Math.round(RTL ? pos : 100 - pos);
    function paint(p) {
      pos = Math.max(0, Math.min(100, p));
      root.style.setProperty("--pos", pos + "%");
      handle.setAttribute("aria-valuenow", String(afterShare()));
      handle.setAttribute("aria-valuetext", `${T.after || "After"} ${digits(afterShare())}%`);
    }
    // Critically-damped follow: fast near the cursor, never overshoots.
    function springTo(p) {
      target = Math.max(0, Math.min(100, p));
      if (reduceMotion) { paint(target); return; }
      if (raf) return;
      const tick = () => {
        const next = pos + (target - pos) * 0.18;
        if (Math.abs(target - next) < 0.05) { paint(target); raf = null; return; }
        paint(next);
        raf = requestAnimationFrame(tick);
      };
      raf = requestAnimationFrame(tick);
    }
    const pctFrom = (e) => { const r = root.getBoundingClientRect(); return ((e.clientX - r.left) / r.width) * 100; };
    function touched() { root.classList.add("is-touched"); if (introAnim) { cancelAnimationFrame(introAnim); introAnim = null; } }

    root.addEventListener("pointerdown", (e) => {
      if (e.button !== 0) return;
      touched();
      dragging = true;
      root.classList.add("is-dragging");
      root.setPointerCapture(e.pointerId);
      if (raf) { cancelAnimationFrame(raf); raf = null; }
      paint(pctFrom(e));
    });
    root.addEventListener("pointermove", (e) => {
      if (dragging) { paint(pctFrom(e)); return; }
      if (finePointer && e.pointerType === "mouse") { touched(); springTo(pctFrom(e)); }
    });
    root.addEventListener("pointerleave", (e) => {
      if (!dragging && finePointer && e.pointerType === "mouse") springTo(50);
    });
    const end = (e) => {
      if (!dragging) return;
      dragging = false;
      root.classList.remove("is-dragging");
      if (root.hasPointerCapture(e.pointerId)) root.releasePointerCapture(e.pointerId);
    };
    root.addEventListener("pointerup", end);
    root.addEventListener("pointercancel", end);
    handle.addEventListener("keydown", (e) => {
      const map = { ArrowLeft: -2, ArrowRight: 2, PageDown: -10, PageUp: 10 };
      if (e.key in map) { e.preventDefault(); touched(); paint(pos + map[e.key]); }
      else if (e.key === "Home") { e.preventDefault(); paint(0); }
      else if (e.key === "End") { e.preventDefault(); paint(100); }
    });
    paint(50);

    // On touch screens (no hover) one gentle sweep teaches the gesture, then rests.
    if (root.hasAttribute("data-ba-intro") && !reduceMotion && !finePointer) {
      const keys = [[0, 50], [0.42, 30], [0.78, 68], [1, 50]];
      const duration = 2400, delay = 700;
      const ease = (t) => 1 - Math.pow(1 - t, 3);
      let start = null;
      const step = (ts) => {
        if (start === null) start = ts + delay;
        const t = Math.min(1, Math.max(0, (ts - start) / duration));
        for (let i = 1; i < keys.length; i++) {
          if (t <= keys[i][0]) {
            const [t0, p0] = keys[i - 1], [t1, p1] = keys[i];
            paint(p0 + (p1 - p0) * ease((t - t0) / (t1 - t0)));
            break;
          }
        }
        introAnim = t < 1 ? requestAnimationFrame(step) : null;
      };
      const io = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) { introAnim = requestAnimationFrame(step); io.disconnect(); }
      }, { threshold: 0.5 });
      io.observe(root);
    }
  }
  $$("[data-ba]").forEach(initSlider);

  /* Hero: a soft light follows the cursor across the panel. */
  const hero = $("[data-hero]");
  if (hero && finePointer && !reduceMotion) {
    let frame = null, mx = 50, my = 20;
    hero.addEventListener("pointermove", (e) => {
      const r = hero.getBoundingClientRect();
      mx = ((e.clientX - r.left) / r.width) * 100;
      my = ((e.clientY - r.top) / r.height) * 100;
      if (frame) return;
      frame = requestAnimationFrame(() => {
        hero.style.setProperty("--mx", mx.toFixed(1) + "%");
        hero.style.setProperty("--my", my.toFixed(1) + "%");
        frame = null;
      });
    });
  }

  /* ───────────── Jalali calendar (port of jalaali-js) ───────────── */
  const J = (function () {
    const div = (a, b) => ~~(a / b);
    const mod = (a, b) => a - ~~(a / b) * b;
    const BREAKS = [-61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210, 1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178];
    function jalCal(jy) {
      const gy = jy + 621;
      let leapJ = -14, jp = BREAKS[0], jump = 0;
      for (let i = 1; i < BREAKS.length; i++) {
        const jm = BREAKS[i];
        jump = jm - jp;
        if (jy < jm) break;
        leapJ += div(jump, 33) * 8 + div(mod(jump, 33), 4);
        jp = jm;
      }
      let n = jy - jp;
      leapJ += div(n, 33) * 8 + div(mod(n, 33) + 3, 4);
      if (mod(jump, 33) === 4 && jump - n === 4) leapJ += 1;
      const leapG = div(gy, 4) - div((div(gy, 100) + 1) * 3, 4) - 150;
      const march = 20 + leapJ - leapG;
      if (jump - n < 6) n = n - jump + div(jump + 4, 33) * 33;
      let leap = mod(mod(n + 1, 33) - 1, 4);
      if (leap === -1) leap = 4;
      return { leap, gy, march };
    }
    function g2d(gy, gm, gd) {
      let d = div((gy + div(gm - 8, 6) + 100100) * 1461, 4) + div(153 * mod(gm + 9, 12) + 2, 5) + gd - 34840408;
      return d - div(div(gy + 100100 + div(gm - 8, 6), 100) * 3, 4) + 752;
    }
    function d2g(jdn) {
      let j = 4 * jdn + 139361631;
      j = j + div(div(4 * jdn + 183187720, 146097) * 3, 4) * 4 - 3908;
      const i = div(mod(j, 1461), 4) * 5 + 308;
      const gd = div(mod(i, 153), 5) + 1;
      const gm = mod(div(i, 153), 12) + 1;
      const gy = div(j, 1461) - 100100 + div(8 - gm, 6);
      return [gy, gm, gd];
    }
    function j2d(jy, jm, jd) {
      const r = jalCal(jy);
      return g2d(r.gy, 3, r.march) + (jm - 1) * 31 - div(jm, 7) * (jm - 7) + jd - 1;
    }
    function d2j(jdn) {
      const gy = d2g(jdn)[0];
      let jy = gy - 621;
      const r = jalCal(jy);
      let k = jdn - g2d(gy, 3, r.march);
      if (k >= 0) {
        if (k <= 185) return [jy, 1 + div(k, 31), mod(k, 31) + 1];
        k -= 186;
      } else {
        jy -= 1; k += 179;
        if (r.leap === 1) k += 1;
      }
      return [jy, 7 + div(k, 30), mod(k, 30) + 1];
    }
    return {
      toJ: (gy, gm, gd) => d2j(g2d(gy, gm, gd)),
      toG: (jy, jm, jd) => d2g(j2d(jy, jm, jd)),
      monthLen: (jy, jm) => (jm <= 6 ? 31 : jm <= 11 ? 30 : jalCal(jy).leap === 0 ? 30 : 29),
    };
  })();

  const NAMES = {
    fa: {
      months: ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"],
      wd: ["ی", "د", "س", "چ", "پ", "ج", "ش"],
      wdLong: ["یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه"],
      first: 6,
    },
    ar: {
      months: ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
      wd: ["ح", "ن", "ث", "ر", "خ", "ج", "س"],
      wdLong: ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"],
      first: 6,
    },
    en: {
      months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
      wd: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
      wdLong: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
      first: 0,
    },
  };
  const N = NAMES[LANG] || NAMES.en;
  const JALALI = LANG === "fa";
  const parseISO = (s) => s.split("-").map(Number);
  const weekday = (y, m, d) => new Date(Date.UTC(y, m - 1, d)).getUTCDay();
  const gDaysInMonth = (y, m) => new Date(Date.UTC(y, m, 0)).getUTCDate();

  /** Human label for an ISO (Gregorian) date in the active language. */
  function dateLabel(isoStr) {
    const [y, m, d] = parseISO(isoStr);
    const wd = N.wdLong[weekday(y, m, d)];
    if (JALALI) {
      const [jy, jm, jd] = J.toJ(y, m, d);
      return digits(`${wd} ${jd} ${N.months[jm - 1]} ${jy}`);
    }
    if (LANG === "ar") return digits(`${wd} ${d} ${N.months[m - 1]} ${y}`);
    return `${wd}, ${N.months[m - 1]} ${d}, ${y}`;
  }

  class DatePicker {
    constructor(field, onPick) {
      this.trigger = $("[data-date-trigger]", field);
      this.panel = $("[data-datepicker]", field);
      this.onPick = onPick;
      this.today = CFG.booking.today;
      this.max = CFG.booking.maxDate;
      this.closed = CFG.booking.closedDays || [];
      this.value = "";
      const [y, m, d] = parseISO(this.today);
      [this.vy, this.vm] = JALALI ? J.toJ(y, m, d) : [y, m];
      this.focusISO = this.today;
      this.trigger.addEventListener("click", () => (this.panel.hidden ? this.open() : this.close()));
      document.addEventListener("click", (e) => { if (!field.contains(e.target)) this.close(); });
      this.panel.addEventListener("keydown", (e) => this.onKey(e));
    }
    disabled(isoStr) {
      if (isoStr < this.today || isoStr > this.max) return true;
      const [y, m, d] = parseISO(isoStr);
      return this.closed.includes(weekday(y, m, d));
    }
    // Calendar month (in the active calendar system) → list of ISO dates
    monthDays() {
      const days = [];
      if (JALALI) {
        const len = J.monthLen(this.vy, this.vm);
        for (let d = 1; d <= len; d++) { const [gy, gm, gd] = J.toG(this.vy, this.vm, d); days.push(iso(gy, gm, gd)); }
      } else {
        for (let d = 1; d <= gDaysInMonth(this.vy, this.vm); d++) days.push(iso(this.vy, this.vm, d));
      }
      return days;
    }
    shift(delta) {
      this.vm += delta;
      if (this.vm < 1) { this.vm = 12; this.vy -= 1; }
      if (this.vm > 12) { this.vm = 1; this.vy += 1; }
    }
    render() {
      const days = this.monthDays();
      const [fy, fm, fd] = parseISO(days[0]);
      const lead = (weekday(fy, fm, fd) - N.first + 7) % 7;
      const canPrev = days[0] > this.today;
      const canNext = days[days.length - 1] < this.max;
      const title = `${N.months[this.vm - 1]} ${digits(this.vy)}`;
      let html = `<div class="dp__head"><span class="dp__title" aria-live="polite">${title}</span><div class="dp__nav">`;
      const prevIc = RTL ? "M9 6l6 6-6 6" : "M15 6l-6 6 6 6";
      const nextIc = RTL ? "M15 6l-6 6 6 6" : "M9 6l6 6-6 6";
      html += `<button type="button" data-dp="prev" aria-label="${T.prevMonth}" ${canPrev ? "" : "disabled"}><svg class="ic" viewBox="0 0 24 24"><path d="${prevIc}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button>`;
      html += `<button type="button" data-dp="next" aria-label="${T.nextMonth}" ${canNext ? "" : "disabled"}><svg class="ic" viewBox="0 0 24 24"><path d="${nextIc}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button>`;
      html += `</div></div><div class="dp__grid" role="grid">`;
      for (let i = 0; i < 7; i++) html += `<span class="dp__wd" aria-hidden="true">${N.wd[(N.first + i) % 7]}</span>`;
      for (let i = 0; i < lead; i++) html += "<span></span>";
      if (!days.includes(this.focusISO)) {
        this.focusISO = days.find((d) => !this.disabled(d)) || days[0];
      }
      days.forEach((d, idx) => {
        const dis = this.disabled(d);
        const sel = d === this.value;
        const cls = "dp__day" + (d === this.today ? " is-today" : "");
        html += `<button type="button" class="${cls}" data-date="${d}" aria-label="${dateLabel(d)}${dis ? " — " + T.closed : ""}"` +
          ` aria-selected="${sel}" tabindex="${d === this.focusISO ? 0 : -1}" ${dis ? "disabled" : ""}>${digits(idx + 1)}</button>`;
      });
      html += `</div><p class="dp__foot">${T.today}</p>`;
      this.panel.innerHTML = html;
      $$("[data-dp]", this.panel).forEach((b) => b.addEventListener("click", (e) => {
        e.stopPropagation();
        this.shift(b.dataset.dp === "next" ? 1 : -1);
        this.render();
      }));
      $$("[data-date]", this.panel).forEach((b) => b.addEventListener("click", () => this.pick(b.dataset.date)));
    }
    open() {
      this.render();
      this.panel.hidden = false;
      this.trigger.setAttribute("aria-expanded", "true");
      const f = $(`[data-date="${this.focusISO}"]`, this.panel);
      if (f && !f.disabled) f.focus();
    }
    close() {
      if (this.panel.hidden) return;
      this.panel.hidden = true;
      this.trigger.setAttribute("aria-expanded", "false");
    }
    pick(isoStr) {
      this.value = isoStr;
      this.focusISO = isoStr;
      this.close();
      this.trigger.focus();
      this.onPick(isoStr);
    }
    reset() { this.value = ""; }
    onKey(e) {
      if (e.key === "Escape") { e.preventDefault(); this.close(); this.trigger.focus(); return; }
      const btn = e.target.closest("[data-date]");
      if (!btn) return;
      const delta = { ArrowLeft: RTL ? 1 : -1, ArrowRight: RTL ? -1 : 1, ArrowUp: -7, ArrowDown: 7 }[e.key];
      if (!delta) return;
      e.preventDefault();
      const [y, m, d] = parseISO(btn.dataset.date);
      const next = new Date(Date.UTC(y, m - 1, d + delta));
      const nextISO = iso(next.getUTCFullYear(), next.getUTCMonth() + 1, next.getUTCDate());
      if (nextISO < this.today || nextISO > this.max) return;
      this.focusISO = nextISO;
      if (!$(`[data-date="${nextISO}"]`, this.panel)) {
        this.shift(delta > 0 ? 1 : -1);
        this.render();
      } else {
        $$("[data-date]", this.panel).forEach((b) => (b.tabIndex = b.dataset.date === nextISO ? 0 : -1));
      }
      const target = $(`[data-date="${nextISO}"]`, this.panel);
      if (target) target.focus();
    }
  }

  /* ───────────── page context (what the visitor is looking at) ───────────── */
  let currentSection = "";
  const sectionEls = $$(".p-section[id], main section[aria-labelledby]");
  if (sectionEls.length && "IntersectionObserver" in window) {
    const titleOf = (el) => {
      const h = el.matches("[aria-labelledby]") ? document.getElementById(el.getAttribute("aria-labelledby")) : $("h2", el);
      return h ? h.textContent.trim().replace(/\s+/g, " ") : "";
    };
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        currentSection = en.target.id === "main" ? "" : titleOf(en.target);
        $$(".toc a").forEach((a) => a.classList.toggle("is-active", a.getAttribute("href") === "#" + en.target.id));
        const active = $(".toc a.is-active");
        if (active) active.scrollIntoView({ block: "nearest", inline: "center", behavior: reduceMotion ? "auto" : "smooth" });
        updateChatContext();
      });
    }, { rootMargin: "-35% 0px -60% 0px" });
    sectionEls.forEach((el) => io.observe(el));
  }
  function pageContext() {
    return {
      title: PAGE.title || document.title,
      url: location.pathname + location.search,
      type: PAGE.type || "",
      procedure: PAGE.procedure || "",
      category: PAGE.category || "",
      section: currentSection,
      lang: LANG,
    };
  }

  /* ───────────── booking forms ───────────── */
  function initBookingForm(form) {
    const body = $("[data-form-body]", form);
    const done = $("[data-form-done]", form);
    const dateValue = $("[data-date-value]", form);
    const slotValue = $("[data-slot-value]", form);
    const dateText = $("[data-date-text]", form);
    const dateBtn = $("[data-date-trigger]", form);
    const slotsBox = $("[data-slots]", form);
    const submit = $("[data-submit]", form);
    const formError = $("[data-form-error]", form);

    const setError = (name, msg) => {
      const p = $(`[data-error-for="${name}"]`, form);
      if (p) p.textContent = msg || "";
      const input = form.elements[name];
      const target = name === "preferred_date" ? dateBtn : input && input.type !== "hidden" ? input : null;
      if (target) target.setAttribute("aria-invalid", msg ? "true" : "false");
    };
    const clearErrors = () => {
      $$("[data-error-for]", form).forEach((p) => (p.textContent = ""));
      $$("[aria-invalid]", form).forEach((el) => el.setAttribute("aria-invalid", "false"));
      formError.textContent = "";
    };

    function renderSlots(list) {
      slotsBox.innerHTML = "";
      if (!list.length) {
        slotsBox.innerHTML = `<p class="slots__hint">${T.noSlots}</p>`;
        return;
      }
      list.forEach((s) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "slot";
        b.setAttribute("role", "radio");
        b.setAttribute("aria-checked", "false");
        b.dataset.time = s.time;
        b.textContent = s.label;
        b.disabled = !s.available;
        b.tabIndex = -1;
        b.addEventListener("click", () => chooseSlot(b));
        slotsBox.appendChild(b);
      });
      const first = $(".slot:not(:disabled)", slotsBox);
      if (first) first.tabIndex = 0; else slotsBox.innerHTML = `<p class="slots__hint">${T.noSlots}</p>`;
    }
    function chooseSlot(btn) {
      $$(".slot", slotsBox).forEach((b) => { b.setAttribute("aria-checked", String(b === btn)); b.tabIndex = b === btn ? 0 : -1; });
      slotValue.value = btn.dataset.time;
      setError("time_slot", "");
    }
    slotsBox.addEventListener("keydown", (e) => {
      const opts = $$(".slot:not(:disabled)", slotsBox);
      const i = opts.indexOf(document.activeElement);
      if (i < 0) return;
      const step = { ArrowRight: RTL ? -1 : 1, ArrowLeft: RTL ? 1 : -1, ArrowDown: 1, ArrowUp: -1 }[e.key];
      if (!step) return;
      e.preventDefault();
      const next = opts[(i + step + opts.length) % opts.length];
      next.focus(); chooseSlot(next);
    });

    async function loadSlots(isoStr) {
      slotValue.value = "";
      slotsBox.classList.add("is-loading");
      slotsBox.innerHTML = `<p class="slots__hint">${T.loadingSlots}</p>`;
      const res = await api(`${CFG.urls.slots}?date=${isoStr}`).catch(() => ({ ok: false }));
      slotsBox.classList.remove("is-loading");
      if (!res.ok) { slotsBox.innerHTML = `<p class="slots__hint">${T.network}</p>`; return; }
      renderSlots(res.data.slots || []);
    }

    const picker = new DatePicker($("[data-datefield]", form), (isoStr) => {
      dateValue.value = isoStr;
      dateText.textContent = dateLabel(isoStr);
      dateBtn.classList.add("has-value");
      setError("preferred_date", "");
      loadSlots(isoStr);
    });

    $$("input, select, textarea", form).forEach((el) =>
      el.addEventListener("input", () => { if (el.name) setError(el.name, ""); }));

    function validate() {
      clearErrors();
      let ok = true;
      const req = (name, msg) => { if (!String(form.elements[name].value).trim()) { setError(name, msg || T.required); ok = false; } };
      req("procedure"); req("full_name"); req("phone");
      if (!dateValue.value) { setError("preferred_date", T.pickDate); ok = false; }
      else if (!slotValue.value) { setError("time_slot", T.pickTime); ok = false; }
      if (!ok) {
        const firstBad = $("[aria-invalid=true]", form);
        if (firstBad) firstBad.focus();
      }
      return ok;
    }

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!validate()) return;
      const ctx = pageContext();
      $("[data-source-url]", form).value = ctx.url;
      $("[data-source-title]", form).value = (ctx.title + (ctx.section ? " — " + ctx.section : "")).slice(0, 200);
      submit.setAttribute("aria-busy", "true");
      const label = submit.innerHTML;
      submit.innerHTML = `<span>${T.sending}</span>`;
      let res;
      try {
        res = await api(CFG.urls.submit, { method: "POST", body: new FormData(form) });
      } catch (err) {
        res = { ok: false, data: { errors: { __all__: [T.network] } } };
      }
      submit.removeAttribute("aria-busy");
      submit.innerHTML = label;
      if (!res.ok) {
        const errs = (res.data && res.data.errors) || { __all__: [T.network] };
        Object.keys(errs).forEach((k) => {
          if (k === "__all__" || !$(`[data-error-for="${k}"]`, form)) formError.textContent = errs[k].join(" ");
          else setError(k, errs[k].join(" "));
        });
        if (errs.time_slot && dateValue.value) loadSlots(dateValue.value);
        return;
      }
      const d = res.data;
      $("[data-done-text]", form).textContent = [d.procedure, d.date, d.time].filter(Boolean).join(" · ");
      $("[data-done-code]", form).textContent = d.code;
      body.hidden = true;
      done.hidden = false;
      done.focus();
    });

    $("[data-form-reset]", form).addEventListener("click", () => {
      form.reset();
      picker.reset();
      dateValue.value = slotValue.value = "";
      dateText.textContent = T.pickDate;
      dateBtn.classList.remove("has-value");
      slotsBox.innerHTML = `<p class="slots__hint">${T.pickDateFirst}</p>`;
      clearErrors();
      done.hidden = true;
      body.hidden = false;
      $("select, input:not([type=hidden])", body).focus();
    });
    form.resetToBody = () => { if (!done.hidden) $("[data-form-reset]", form).click(); };
  }
  $$("[data-booking-form]").forEach(initBookingForm);

  /* Booking dialog — opened by every "Book" button, optionally preselecting a treatment */
  const dialog = $("[data-booking-dialog]");
  if (dialog) {
    const form = $("[data-booking-form]", dialog);
    const close = () => { dialog.close(); };
    dialog.addEventListener("close", () => document.body.classList.remove("has-modal"));
    dialog.addEventListener("click", (e) => { if (e.target === dialog) close(); });
    $("[data-close-dialog]", dialog).addEventListener("click", close);
    $$("[data-open-booking]").forEach((btn) => btn.addEventListener("click", () => {
      if (form.resetToBody) form.resetToBody();
      const id = btn.dataset.openBooking;
      if (id) $("[data-procedure-select]", form).value = id;
      else if (PAGE.type !== "procedure") $("[data-procedure-select]", form).value = form.dataset.defaultProcedure || "";
      if (typeof dialog.showModal === "function") dialog.showModal(); else dialog.setAttribute("open", "");
      document.body.classList.add("has-modal");
      const first = id ? $("input[name=full_name]", form) : $("[data-procedure-select]", form);
      setTimeout(() => first.focus(), 30);
    }));
    // On a treatment page, preselect that treatment in the dialog too.
    const pageSelect = $(".p-aside [data-procedure-select]");
    if (pageSelect && pageSelect.value) {
      $("[data-procedure-select]", form).value = pageSelect.value;
      form.dataset.defaultProcedure = pageSelect.value;
    }
  }

  /* ───────────── chat widget ───────────── */
  const chat = $("[data-chat]");
  let updateChatContext = () => {};
  if (chat && CFG.urls) {
    const fab = $("[data-chat-toggle]", chat);
    const panel = $("[data-chat-panel]", chat);
    const badge = $("[data-chat-badge]", chat);
    const startForm = $("[data-chat-start]", chat);
    const threadBox = $("[data-chat-thread]", chat);
    const log = $("[data-chat-log]", chat);
    const compose = $("[data-chat-compose]", chat);
    const ctxText = $("[data-chat-context-text]", chat);
    const errorBox = $("[data-chat-error]", chat);
    const HAS = "rk-chat";
    let lastId = 0;
    let timer = null;
    let hasThread = store.get(HAS) === "1";

    updateChatContext = function () {
      const c = pageContext();
      ctxText.textContent = c.title + (c.section && c.section !== c.title ? ` · ${c.section}` : "");
    };
    updateChatContext();

    const timeLabel = (isoStr) => {
      const d = new Date(isoStr);
      return digits(`${pad(d.getHours())}:${pad(d.getMinutes())}`);
    };
    function addMessage(m) {
      if (m.id <= lastId) return;
      lastId = m.id;
      const li = document.createElement("li");
      li.className = "msg msg--" + (m.sender === "visitor" ? "visitor" : "staff");
      if (m.sender !== "visitor") {
        const n = document.createElement("span");
        n.className = "msg__name";
        n.textContent = m.name || T.clinic;
        li.appendChild(n);
      }
      const bd = document.createElement("span"); bd.className = "msg__body"; bd.textContent = m.body; li.appendChild(bd);
      const t = document.createElement("span");
      t.className = "msg__time";
      t.textContent = timeLabel(m.at);
      li.appendChild(t);
      log.appendChild(li);
      log.scrollTop = log.scrollHeight;
    }
    function showThread() { startForm.hidden = true; threadBox.hidden = false; }
    function showStart() { startForm.hidden = false; threadBox.hidden = true; log.innerHTML = ""; lastId = 0; }
    const setBadge = (n) => { badge.hidden = !n; badge.textContent = digits(n); };

    async function poll(seen) {
      const res = await api(`${CFG.urls.chatState}?after=${lastId}${seen ? "&seen=1" : ""}`).catch(() => null);
      if (!res || !res.ok) return;
      if (!res.data.thread) { hasThread = false; store.del(HAS); showStart(); return; }
      hasThread = true;
      showThread();
      (res.data.messages || []).forEach(addMessage);
      setBadge(panel.hidden ? res.data.unread : 0);
    }
    function schedule() {
      clearTimeout(timer);
      if (!hasThread || document.hidden) return;
      timer = setTimeout(async () => { await poll(!panel.hidden); schedule(); }, panel.hidden ? 25000 : 4000);
    }
    document.addEventListener("visibilitychange", () => { if (!document.hidden) schedule(); });

    function open(recipient) {
      panel.hidden = false;
      chat.classList.add("is-open");
      fab.setAttribute("aria-expanded", "true");
      updateChatContext();
      if (recipient && !hasThread) {
        const r = $(`input[name=recipient][value=${recipient}]`, startForm);
        if (r) r.checked = true;
      }
      if (hasThread) { poll(true).then(() => { schedule(); $("textarea", compose).focus(); }); }
      else $("#chat-name").focus();
    }
    function close() {
      panel.hidden = true;
      chat.classList.remove("is-open");
      fab.setAttribute("aria-expanded", "false");
      fab.focus();
      schedule();
    }
    fab.addEventListener("click", () => open());
    $("[data-chat-close]", chat).addEventListener("click", close);
    panel.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
    $$("[data-open-chat]").forEach((b) => b.addEventListener("click", () => open(b.dataset.openChat)));

    startForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      $$("[data-error-for]", startForm).forEach((p) => (p.textContent = ""));
      errorBox.textContent = "";
      const fd = new FormData(startForm);
      const payload = {
        recipient: fd.get("recipient"), name: fd.get("name"), phone: fd.get("phone"),
        body: fd.get("body"), context: pageContext(),
      };
      let bad = false;
      if (!String(payload.name).trim()) { $('[data-error-for="name"]', startForm).textContent = T.required; bad = true; }
      if (!String(payload.body).trim()) { $('[data-error-for="body"]', startForm).textContent = T.required; bad = true; }
      if (bad) return;
      const btn = $("button[type=submit]", startForm);
      btn.disabled = true;
      const res = await api(CFG.urls.chatStart, { method: "POST", json: payload }).catch(() => ({ ok: false, data: {} }));
      btn.disabled = false;
      if (!res.ok) {
        const errs = res.data.errors || {};
        Object.keys(errs).forEach((k) => { const p = $(`[data-error-for="${k}"]`, startForm); if (p) p.textContent = errs[k]; });
        if (!Object.keys(errs).length) errorBox.textContent = res.data.error || T.network;
        return;
      }
      hasThread = true;
      store.set(HAS, "1");
      startForm.reset();
      showThread();
      (res.data.messages || []).forEach(addMessage);
      $("textarea", compose).focus();
      schedule();
    });

    const input = $("textarea", compose);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); compose.requestSubmit(); }
    });
    input.addEventListener("input", () => { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 120) + "px"; });
    compose.addEventListener("submit", async (e) => {
      e.preventDefault();
      const body = input.value.trim();
      if (!body) return;
      input.value = "";
      input.style.height = "";
      const res = await api(CFG.urls.chatSend, { method: "POST", json: { body, context: pageContext() } }).catch(() => ({ ok: false, data: {} }));
      if (res.ok) addMessage(res.data.message);
      else if (res.status === 404) { hasThread = false; store.del(HAS); showStart(); }
      else { input.value = body; }
    });
    $("[data-chat-reset]", chat).addEventListener("click", async () => {
      await api(CFG.urls.chatReset, { method: "POST" }).catch(() => null);
      hasThread = false; store.del(HAS); showStart(); clearTimeout(timer);
      $("#chat-name").focus();
    });

    if (hasThread) poll(false).then(schedule);
  }

  /* ───────────── procedure page: mobile booking bar ───────────── */
  const bar = $("[data-mobile-book]");
  const aside = $(".p-aside");
  if (bar && aside && "IntersectionObserver" in window) {
    const footer = $(".site-footer");
    const seen = new Set();
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => (en.isIntersecting ? seen.add(en.target) : seen.delete(en.target)));
      bar.classList.toggle("is-away", seen.size > 0);
    });
    io.observe(aside);
    if (footer) io.observe(footer);
  }
})();
