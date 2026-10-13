/* Rokhsar clinic — staff panel behaviour */
(function () {
  "use strict";
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  let CFG = {};
  try { CFG = JSON.parse($("#pn-config").textContent); } catch (e) { /* login page */ }
  const LANG = CFG.lang || document.documentElement.lang;
  const FA = "۰۱۲۳۴۵۶۷۸۹", AR = "٠١٢٣٤٥٦٧٨٩";
  const digits = (v) => String(v).replace(/\d/g, (d) => (LANG === "fa" ? FA[d] : LANG === "ar" ? AR[d] : d));
  const csrf = () => { const m = document.cookie.match(/(?:^|; )csrftoken=([^;]*)/); return m ? decodeURIComponent(m[1]) : ($("input[name=csrfmiddlewaretoken]") || {}).value; };
  const pad = (n) => String(n).padStart(2, "0");

  // Theme
  $$("[data-theme-toggle]").forEach((b) => b.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("rk-theme", next); } catch (e) { /* ignore */ }
  }));

  // Live badges + toast for new requests
  if (CFG.pulse) {
    let since = new Date().toISOString();
    let lastUnread = null;
    const toast = $("[data-toast]");
    const showToast = (text) => {
      $("[data-toast-text]", toast).textContent = text;
      toast.hidden = false;
      clearTimeout(showToast.t);
      showToast.t = setTimeout(() => (toast.hidden = true), 9000);
    };
    async function pulse() {
      try {
        const res = await fetch(`${CFG.pulse}?since=${encodeURIComponent(since)}`, { credentials: "same-origin" });
        if (!res.ok) return;
        const d = await res.json();
        since = d.now;
        $$("[data-pulse]").forEach((b) => { const n = d[b.dataset.pulse] || 0; b.hidden = !n; b.textContent = digits(n); });
        if (d.new_bookings) showToast(`${CFG.newBooking} (${digits(d.new_bookings)})`);
        else if (lastUnread !== null && d.unread_chats > lastUnread) showToast(CFG.newChat);
        lastUnread = d.unread_chats;
        document.title = document.title.replace(/^\(\S+\) /, "");
        const total = d.pending + d.unread_chats;
        if (total) document.title = `(${digits(total)}) ${document.title}`;
      } catch (e) { /* offline — try again later */ }
    }
    pulse();
    setInterval(() => { if (!document.hidden) pulse(); }, 15000);
  }

  // Inline status change on the appointments table
  $$("[data-status-form]").forEach((form) => {
    const select = $("[data-status-select]", form);
    const wrap = $("[data-status-wrap]", form);
    select.addEventListener("change", async () => {
      const body = new FormData(form);   // read before disabling, or the value is dropped
      select.disabled = true;
      try {
        const res = await fetch(form.action, {
          method: "POST", credentials: "same-origin", headers: { "X-CSRFToken": csrf() }, body,
        });
        const d = await res.json();
        if (d.ok) wrap.className = `select select--pill pill--${d.tone}`;
      } finally { select.disabled = false; }
    });
  });

  // Channel form: show only the fields that matter for the selected type
  const chForm = $("[data-channel-form]");
  if (chForm) {
    const NEED = {
      telegram: ["token", "target", "api_base", "proxy_url", "allow_replies"],
      bale: ["token", "target", "api_base", "proxy_url", "allow_replies"],
      eitaa: ["token", "target", "api_base", "proxy_url"],
      whatsapp: ["token", "target", "sender_id", "api_base", "proxy_url"],
      email: ["target"],
      webhook: ["token", "target", "proxy_url"],
    };
    const OPTIONAL = ["token", "target", "sender_id", "api_base", "proxy_url", "allow_replies"];
    const kind = $("select[name=kind]", chForm);
    const sync = () => {
      const need = NEED[kind.value] || OPTIONAL;
      OPTIONAL.forEach((name) => { const f = $(`[data-field="${name}"]`, chForm); if (f) f.classList.toggle("is-hidden", !need.includes(name)); });
    };
    kind.addEventListener("change", sync);
    sync();
  }

  // Conversation: live updates and replies
  const log = $("[data-thread-log]");
  const compose = $("[data-thread-compose]");
  if (log && compose) {
    const api = log.dataset.api;
    const idOf = (li) => Number(li.dataset.id || 0);
    let lastId = Math.max(0, ...$$("[data-id]", log).map(idOf));
    let lastCtx = "";
    log.scrollTop = log.scrollHeight;
    const time = (iso) => { const d = new Date(iso); return digits(`${pad(d.getHours())}:${pad(d.getMinutes())}`); };

    function add(m) {
      if (m.id <= lastId) return;
      lastId = m.id;
      const ctx = m.context || {};
      const key = `${ctx.url || ""}|${ctx.section || ""}`;
      if (m.sender === "visitor" && ctx.title && key !== lastCtx) {
        const mk = document.createElement("li");
        mk.className = "thread__marker";
        mk.textContent = `${log.dataset.seenLabel}: ${ctx.title}${ctx.section ? " · " + ctx.section : ""}`;
        log.appendChild(mk);
        lastCtx = key;
      }
      const li = document.createElement("li");
      li.className = "msg msg--" + (m.sender === "visitor" ? "in" : "out");
      li.dataset.id = m.id;
      if (m.sender !== "visitor") {
        const n = document.createElement("span"); n.className = "msg__name"; n.textContent = m.name || ""; li.appendChild(n);
      }
      const bd = document.createElement("span"); bd.className = "msg__body"; bd.textContent = m.body; li.appendChild(bd);
      const t = document.createElement("span"); t.className = "msg__time"; t.textContent = time(m.at); li.appendChild(t);
      log.appendChild(li);
      log.scrollTop = log.scrollHeight;
    }
    function setCtx(ctx) {
      if (!ctx) return;
      const title = $("[data-ctx-title]"), link = $("[data-ctx-link]"), sec = $("[data-ctx-section]");
      if (title && ctx.title) title.textContent = ctx.title;
      if (link && ctx.url) link.href = ctx.url;
      if (sec) sec.textContent = ctx.section ? ` · ${log.dataset.sectionLabel}: ${ctx.section}` : "";
    }
    async function poll() {
      try {
        const res = await fetch(`${api}?after=${lastId}`, { credentials: "same-origin" });
        const d = await res.json();
        (d.messages || []).forEach(add);
        setCtx(d.context);
      } catch (e) { /* retry */ }
    }
    setInterval(() => { if (!document.hidden) poll(); }, 4000);

    const input = $("textarea", compose);
    input.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); compose.requestSubmit(); } });
    input.addEventListener("input", () => { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 140) + "px"; });
    compose.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!input.value.trim()) return;
      const fd = new FormData(compose);
      input.value = ""; input.style.height = "";
      const res = await fetch(compose.action, { method: "POST", credentials: "same-origin", headers: { "X-CSRFToken": csrf() }, body: fd });
      const d = await res.json().catch(() => ({}));
      if (d.ok) add(d.message); else input.value = fd.get("body");
    });
  }
})();
