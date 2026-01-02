KB_SCRIPT = r"""
<script>
(function(){
  const wrap = document.querySelector('[data-kb-wrap="1"]');
  if(!wrap) return;

  const qEl = wrap.querySelector('[data-kb-filter="q"]');
  const statusEl = wrap.querySelector('[data-kb-filter="status"]');
  const fromEl = wrap.querySelector('[data-kb-filter="from"]');
  const toEl = wrap.querySelector('[data-kb-filter="to"]');

  const archEl = wrap.querySelector('[data-kb-toggle="archived"]');
  const onlyArchEl = wrap.querySelector('[data-kb-toggle="onlyarchived"]');

  const tagBtns = Array.from(wrap.querySelectorAll('[data-kb-tag]'));

  const cols = Array.from(wrap.querySelectorAll('.kb-col'));
  const activeTags = new Set();

  function norm(s){ return (s||"").toString().trim().toLowerCase(); }

  function applyArchiveModes(){
    const only = !!(onlyArchEl && onlyArchEl.checked);

    // ✅ Si "Solo archivados" está activo, fuerza mostrar archivados y oculta el resto
    wrap.classList.toggle('kb-only-archived', only);

    const show = !!(archEl && archEl.checked);
    wrap.classList.toggle('kb-show-archived', show || only);

    // Opcional: bloquear "Ver archivados" cuando solo-archivados está ON
    if(archEl){
      if(only){
        archEl.checked = true;
        archEl.disabled = true;
      } else {
        archEl.disabled = false;
      }
    }
  }

  function parseISO(d){
    if(!d) return null;
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(d);
    if(!m) return null;
    return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])).getTime();
  }

  function anyDateInRange(dates, fromTs, toTs){
    for(const ds of dates){
      const ts = parseISO(ds);
      if(ts === null) continue;
      if(fromTs !== null && ts < fromTs) continue;
      if(toTs !== null && ts > toTs) continue;
      return true;
    }
    return false;
  }

  function applyFilters(){
    const q = norm(qEl && qEl.value);
    const status = (statusEl && statusEl.value) ? statusEl.value : "";
    const fromTs = fromEl && fromEl.value ? parseISO(fromEl.value) : null;
    const toTs = toEl && toEl.value ? parseISO(toEl.value) : null;

    cols.forEach(col => {
      const cards = Array.from(col.querySelectorAll('.kb-card'));
      let visibleCount = 0;

      cards.forEach(card => {
        const title = norm(card.getAttribute('data-title'));
        const tags = (card.getAttribute('data-tags') || "").split(',').filter(Boolean);
        const dates = (card.getAttribute('data-dates') || "").split(',').filter(Boolean);
        const statuses = (card.getAttribute('data-statuses') || "").split(',').filter(Boolean);
        const hasDates = (card.getAttribute('data-hasdates') || "0") === "1";

        const okTitle = !q || title.includes(q);

        let okTag = true;
        if(activeTags.size > 0){
          okTag = tags.some(t => activeTags.has(t));
        }

        let okDate = true;
        if(status === "nodate"){
          okDate = !hasDates;
        } else if(fromTs !== null || toTs !== null){
          okDate = hasDates && anyDateInRange(dates, fromTs, toTs);
        } else if(status){
          okDate = statuses.includes(status);
        }

        const ok = okTitle && okTag && okDate;

        card.classList.toggle('kb-hidden', !ok);
        if(ok) visibleCount++;
      });

      const ph = col.querySelector('[data-kb-empty="filtered"]');
      if(ph){
        ph.style.display = (visibleCount === 0) ? 'block' : 'none';
      }
    });
  }

  // ✅ Tags toggle: al activar se “enciende” (clase is-active)
  tagBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const t = btn.getAttribute('data-kb-tag');
      if(!t) return;
      if(activeTags.has(t)){
        activeTags.delete(t);
        btn.classList.remove('is-active');
      }else{
        activeTags.add(t);
        btn.classList.add('is-active');
      }
      applyFilters();
    });
  });

  function bind(el, ev, cb){
    if(!el) return;
    el.addEventListener(ev, cb);
  }

  // init
  applyArchiveModes();
  applyFilters();

  bind(qEl, 'input', applyFilters);
  bind(statusEl, 'change', applyFilters);
  bind(fromEl, 'change', applyFilters);
  bind(toEl, 'change', applyFilters);

  if(archEl) bind(archEl, 'change', () => { applyArchiveModes(); applyFilters(); });
  if(onlyArchEl) bind(onlyArchEl, 'change', () => { applyArchiveModes(); applyFilters(); });

})();
</script>
"""
    