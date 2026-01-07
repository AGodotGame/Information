KB_STYLE = r"""<style>
:root{
  --kb-border: rgba(0,0,0,.12);
  --kb-col-bg: rgba(0,0,0,.03);
  --kb-col-title-bg: rgba(255,255,255,.70);
  --kb-list-bg: rgba(0,0,0,.05);
  --kb-card-bg: rgba(255,255,255,.92);
  --kb-shadow: rgba(0,0,0,.12);
  --kb-input-bg: rgba(255,255,255,.80);

  --kb-gap: 12px;

  /* ✅ AJUSTA AQUÍ el tamaño global del texto:
     prueba -1px, -2px, -3px... */
  --kb-font-shift: -3px;
}

[data-md-color-scheme="slate"]{
  --kb-border: rgba(255,255,255,.12);
  --kb-col-bg: rgba(255,255,255,.04);
  --kb-col-title-bg: rgba(0,0,0,.18);
  --kb-list-bg: rgba(0,0,0,.22);
  --kb-card-bg: rgba(255,255,255,.06);
  --kb-shadow: rgba(0,0,0,.35);
  --kb-input-bg: rgba(255,255,255,.06);
}

.kb-wrap{ margin: .40rem 0 .85rem; }

/* Toolbar compacto */
.kb-toolbar{
  display:flex;
  justify-content:flex-start;
  flex-wrap:wrap;
  gap:8px;
  margin-bottom:.35rem;
  align-items:center;
}

.kb-field{
  display:flex;
  align-items:center;
  gap:8px;
  border:1px solid var(--kb-border);
  background:var(--kb-input-bg);
  border-radius:12px;
  padding:.22rem .42rem;
}

.kb-field label{
  font-size: calc(.76rem + var(--kb-font-shift));
  opacity:.85;
  white-space:nowrap;
}

.kb-input, .kb-select{
  border:0;
  outline:none;
  background:transparent;
  color:inherit;
  font-size: calc(.84rem + var(--kb-font-shift));
  min-width:120px;
}
.kb-select{ min-width:120px; }

.kb-check{
  display:flex;
  align-items:center;
  gap:8px;
  border:1px solid var(--kb-border);
  background:var(--kb-input-bg);
  border-radius:12px;
  padding:.22rem .50rem;
  cursor:pointer;
  user-select:none;

  font-size: calc(.84rem + var(--kb-font-shift));
}
.kb-check input{ cursor:pointer; }

.kb-hidden{ display:none !important; }

/* Tag bars */
.kb-tagbar{
  display:flex;
  flex-wrap:wrap;
  justify-content:flex-start;
  gap:6px;
  margin-bottom:.35rem;
}

.kb-tagbar-users{
  border:1px solid var(--kb-border);
  background:var(--kb-input-bg);
  border-radius:14px;
  padding:.30rem .35rem;
}

/* filtros siempre coloreados por vars inline */
.kb-tagfilter{
  border-radius:999px;
  border:1px solid var(--kb-border);
  padding:.10rem .42rem;
  font-size: calc(.76rem + var(--kb-font-shift));
  cursor:pointer;
  white-space:nowrap;
  line-height:1.35;
  opacity:.95;
  transition: transform .06s ease, box-shadow .06s ease, opacity .06s ease;

  background-color: var(--tg-bg, transparent);
  color: var(--tg-fg, inherit);
  border-color: var(--tg-fg, var(--kb-border));
}
.kb-tagfilter:hover{
  opacity:1;
  box-shadow:0 6px 16px var(--kb-shadow);
}
.kb-tagfilter.is-active{
  transform: translateY(-1px);
  box-shadow:0 8px 20px var(--kb-shadow);
}

/* ✅ bleed-right como tu versión */
.kb-board.kb-bleed-right{
  --kb-right-bleed: clamp(0px, 18vw, 420px);
  width: calc(100% + var(--kb-right-bleed));
  margin-right: calc(-1 * var(--kb-right-bleed));
}

/* Board */
.kb-board{
  display:flex;
  gap: var(--kb-gap);
  align-items: stretch;
  overflow-x: auto;
  padding-bottom: 7px;
  scroll-snap-type: x proximity;
}

/* ✅ Default: dividir en 4 columnas visibles */
.kb-col{
  flex: 0 0 calc((100% - (var(--kb-gap) * 3)) / 4);
  min-width: 210px;

  background: var(--kb-col-bg);
  border:1px solid var(--kb-border);
  border-radius:14px;
  overflow:hidden;
  display:flex;
  flex-direction:column;
  scroll-snap-align:start;
}

/* ✅ Si se muestra completadas: dividir en 5 columnas visibles */
.kb-wrap.kb-show-done .kb-col{
  flex-basis: calc((100% - (var(--kb-gap) * 4)) / 5);
}

/* En pantallas medianas: anchos fijos (scroll) */
@media (max-width: 1200px){
  .kb-col{ flex: 0 0 240px; min-width: 240px; }
  .kb-input{ min-width:110px; }
  .kb-select{ min-width:110px; }
}

.kb-col-title{
  padding:.42rem .55rem;
  font-weight:750;
  font-size: calc(.90rem + var(--kb-font-shift));
  background:var(--kb-col-title-bg);
  border-bottom:1px solid var(--kb-border);
}

.kb-cards{
  padding:.45rem;
  background:var(--kb-list-bg);
  flex:1;
  display:flex;
  flex-direction:column;
  gap:7px;
}

.kb-empty{
  opacity:.6;
  text-align:center;
  padding:.55rem 0;
}

.kb-card{
  background:var(--kb-card-bg);
  border:1px solid var(--kb-border);
  border-radius:12px;
  padding:.42rem .52rem;
  display:block;
  text-decoration:none;
  color:inherit;
  transition: transform .08s ease, box-shadow .08s ease;
}
.kb-card:hover{ transform: translateY(-1px); box-shadow:0 8px 20px var(--kb-shadow); }
.kb-done{ opacity:.65; }

.kb-card-title{
  font-weight:700;
  margin-bottom:.20rem;
  line-height:1.22;
  font-size: calc(.88rem + var(--kb-font-shift));
}

.kb-meta{ display:flex; flex-wrap:wrap; gap:4px; align-items:center; }

.kb-chip{
  font-size: calc(.70rem + var(--kb-font-shift));
  padding:.05rem .35rem;
  line-height:1.30;
  border-radius:999px;
  border:1px solid var(--kb-border);
  opacity:.95;
}

.kb-date.past{ border-color: rgba(220,60,60,.7); }
.kb-date.soon{ border-color: rgba(255,170,0,.7); }
.kb-date.later{ border-color: rgba(80,160,255,.7); }

/* Archivados ocultos por defecto */
.kb-col.kb-archived{ display:none; }
.kb-wrap.kb-show-archived .kb-col.kb-archived{ display:flex; }

/* ✅ Solo archivados: oculta todo EXCEPTO archived y completadas */
.kb-wrap.kb-only-archived .kb-col:not(.kb-archived):not(.kb-done-col){ display:none !important; }
.kb-wrap.kb-only-archived .kb-col.kb-archived{ display:flex !important; }

/* ✅ Completadas: NO se ve por defecto */
.kb-col.kb-done-col{ display:none !important; }
/* se ve si activas ver completadas */
.kb-wrap.kb-show-done .kb-col.kb-done-col{ display:flex !important; }
/* y también si solo-archivados está ON */
.kb-wrap.kb-only-archived .kb-col.kb-done-col{ display:flex !important; }

/* =========================
   Personas (tags de usuario)
   ========================= */

/* Filtros de usuarios (barra de arriba) */
.kb-tagfilter.kb-userfilter{
  font-weight: 800;
  border-width: 2px;
  padding: .12rem .56rem;
  display: inline-flex;
  align-items: center;
  gap: .35rem;
}

/* “avatar” pequeño delante */
.kb-tagfilter.kb-userfilter::before{
  content:"";
  width: .58em;
  height: .58em;
  border-radius: 999px;
  background: currentColor;
  opacity: .92;
}

/* Chips de usuario dentro de cada tarjeta */
.kb-chip.kb-user{
  display:inline-flex;
  align-items:center;
  gap:.35rem;
  font-weight: 800;
  border-width: 2px;
  padding: .06rem .44rem;
}

/* “avatar” en chips */
.kb-chip.kb-user::before{
  content:"";
  width: .58em;
  height: .58em;
  border-radius: 999px;
  background: currentColor;
  opacity: .92;
}

</style>"""
