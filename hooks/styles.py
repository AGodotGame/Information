KB_STYLE = r"""
<style>
:root{
  --kb-border: rgba(0,0,0,.12);
  --kb-col-bg: rgba(0,0,0,.03);
  --kb-col-title-bg: rgba(255,255,255,.70);
  --kb-list-bg: rgba(0,0,0,.05);
  --kb-card-bg: rgba(255,255,255,.92);
  --kb-shadow: rgba(0,0,0,.12);
  --kb-input-bg: rgba(255,255,255,.80);
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

.kb-wrap{ margin: .6rem 0 1.1rem; }


/* Toolbar */
.kb-toolbar{
  display:flex;
  justify-content: flex-start;  
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: .6rem;
  align-items: center;
}


.kb-field{
  display:flex;
  align-items:center;
  gap: 8px;
  border: 1px solid var(--kb-border);
  background: var(--kb-input-bg);
  border-radius: 14px;
  padding: .4rem .55rem;
}

.kb-field label{
  font-size: .84rem;
  opacity: .85;
  white-space: nowrap;
}

.kb-input, .kb-select{
  border: 0;
  outline: none;
  background: transparent;
  color: inherit;
  font-size: .92rem;
  min-width: 170px;
}

.kb-select{ min-width: 150px; }

.kb-check{
  display:flex;
  align-items:center;
  gap: 8px;
  border: 1px solid var(--kb-border);
  background: var(--kb-input-bg);
  border-radius: 14px;
  padding: .4rem .65rem;
  cursor: pointer;
  user-select: none;
}
.kb-check input{ cursor:pointer; }

.kb-hidden{ display:none !important; }

/* tags chips (toggle) */
.kb-tagbar{
  display:flex;
  flex-wrap: wrap;
  justify-content: flex-start;  
  gap: 8px;
  margin-bottom: .65rem;
}


/* ✅ CAMBIO: por defecto “texto plano”, sin color (apagado) */
.kb-tagfilter{
  border-radius: 999px;
  border: 1px solid var(--kb-border);
  padding: .18rem .55rem;
  font-size: .84rem;
  background: transparent;     /* apagado */
  color: inherit;             /* texto plano */
  cursor: pointer;
  opacity: .7;
  transition: transform .06s ease, box-shadow .06s ease, opacity .06s ease;
}
.kb-tagfilter:hover{
  opacity: .95;
  box-shadow: 0 6px 16px var(--kb-shadow);
}

/* ✅ CAMBIO: “luz encendida” SOLO cuando está activo */
.kb-tagfilter.is-active{
  opacity: 1;
  transform: translateY(-1px);
  box-shadow: 0 8px 20px var(--kb-shadow);
  background: var(--tg-bg);     /* color del tag */
  color: var(--tg-fg);
  border-color: var(--tg-fg);
}

/* bleed derecha */
.kb-board.kb-bleed-right{
  --kb-right-bleed: clamp(0px, 18vw, 420px);
  width: calc(100% + var(--kb-right-bleed));
  margin-right: calc(-1 * var(--kb-right-bleed));
}

/* Board */
.kb-board{
  display:flex;
  gap: 12px;
  align-items: stretch;
  overflow-x: auto;
  padding-bottom: 7px;
  scroll-snap-type: x proximity;
}

/* 5 columnas visibles */
.kb-col{
  flex: 0 0 calc((100% - 48px) / 5);
  min-width: 210px;
  background: var(--kb-col-bg);
  border: 1px solid var(--kb-border);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  scroll-snap-align: start;
}

@media (max-width: 1200px){
  .kb-col{ flex-basis: 280px; }
  .kb-input{ min-width: 130px; }
  .kb-select{ min-width: 130px; }
}

.kb-col-title{
  padding: .6rem .75rem;
  font-weight: 750;
  background: var(--kb-col-title-bg);
  border-bottom: 1px solid var(--kb-border);
}

.kb-cards{
  padding: .65rem;
  background: var(--kb-list-bg);
  flex: 1;
  display:flex;
  flex-direction: column;
  gap: 11px;
}

.kb-empty{
  opacity:.6;
  text-align:center;
  padding:.9rem 0;
}

.kb-card{
  background: var(--kb-card-bg);
  border: 1px solid var(--kb-border);
  border-radius: 14px;
  padding: .62rem .72rem;
  display:block;
  text-decoration:none;
  color: inherit;
  transition: transform .08s ease, box-shadow .08s ease;
}
.kb-card:hover{ transform: translateY(-1px); box-shadow: 0 8px 20px var(--kb-shadow); }
.kb-done{ opacity: .65; }

.kb-card-title{
  font-weight: 700;
  margin-bottom: .4rem;
  line-height: 1.22;
  font-size: .97rem;
}

.kb-meta{ display:flex; flex-wrap:wrap; gap: 6px; }
.kb-chip{
  font-size:.79rem;
  padding:.1rem .48rem;
  border-radius:999px;
  border:1px solid var(--kb-border);
  opacity:.95;
}

.kb-date.past{  border-color: rgba(220,60,60,.7); }
.kb-date.soon{  border-color: rgba(255,170,0,.7); }
.kb-date.later{ border-color: rgba(80,160,255,.7); }

/* Archivados ocultos por defecto */
.kb-col.kb-archived{ display:none; }
.kb-wrap.kb-show-archived .kb-col.kb-archived{ display:flex; }

.kb-wrap.kb-only-archived .kb-col:not(.kb-archived){ display:none !important; }
.kb-wrap.kb-only-archived .kb-col.kb-archived{ display:flex !important; }

.kb-controls{
  width: 100%;
  max-width: 100%;
  margin: 0 0 .65rem 0;
}

</style>
"""
