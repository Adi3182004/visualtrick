import os
import json
import ast
import re

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>VisualTrick Architecture</title>
<script src="https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js"></script>
<script src="https://unpkg.com/dagre@0.8.5/dist/dagre.min.js"></script>
<script src="https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js"></script>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
    width: 100%; height: 100%;
    font-family: Inter, system-ui, Arial;
    background: #020617;
    color: #e5e7eb;
    overflow: hidden;
}

.header {
    padding: 14px 24px;
    background: linear-gradient(90deg, #020617, #0f172a);
    border-bottom: 1px solid #1f2937;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 58px;
    flex-shrink: 0;
}

.header-left { display: flex; flex-direction: column; }
.title   { font-size: 18px; font-weight: 700; letter-spacing: 0.3px; }
.subtitle{ font-size: 11px; opacity: 0.45; margin-top: 2px; }

.header-stats {
    display: flex; gap: 8px; font-size: 11px;
    flex-wrap: wrap; justify-content: flex-end; align-items: center;
}

.stat-pill {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 3px 12px;
    display: flex; align-items: center; gap: 6px;
    white-space: nowrap;
}

.stat-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

#cy { width: 100vw; height: calc(100vh - 58px); display: block; }

.hamburger-btn {
    position: fixed;
    right: 18px; bottom: 18px;
    width: 42px; height: 42px;
    background: rgba(15,23,42,0.95);
    border: 1px solid #334155;
    border-radius: 10px;
    cursor: pointer;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 5px;
    z-index: 30;
    backdrop-filter: blur(10px);
    transition: background 0.15s, border-color 0.15s;
    user-select: none;
}
.hamburger-btn:hover { background: #1e293b; border-color: #475569; }
.hamburger-btn.open  { border-color: #6366f1; background: #1e1b4b; }

.ham-bar {
    width: 18px; height: 2px;
    background: #e5e7eb;
    border-radius: 2px;
    transition: all 0.25s;
}
.hamburger-btn.open .ham-bar:nth-child(1) { transform: translateY(7px) rotate(45deg); }
.hamburger-btn.open .ham-bar:nth-child(2) { opacity: 0; transform: scaleX(0); }
.hamburger-btn.open .ham-bar:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

.legend-panel {
    position: fixed;
    right: 18px; bottom: 70px;
    background: rgba(10,15,30,0.97);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px 18px;
    font-size: 12px;
    line-height: 2.2;
    backdrop-filter: blur(12px);
    z-index: 29;
    min-width: 210px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    opacity: 0;
    transform: translateY(12px) scale(0.97);
    pointer-events: none;
    transition: opacity 0.2s ease, transform 0.2s ease;
}
.legend-panel.open {
    opacity: 1;
    transform: translateY(0) scale(1);
    pointer-events: all;
}

.legend-section-title {
    font-size: 10px;
    opacity: 0.45;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.legend-gap { margin-top: 8px; }

.legend-dot {
    display: inline-block;
    width: 11px; height: 11px;
    border-radius: 50%;
    margin-right: 8px;
    vertical-align: middle;
}

.legend-line {
    display: inline-block;
    width: 22px; height: 3px;
    margin-right: 8px;
    vertical-align: middle;
    border-radius: 2px;
}

.cy-tooltip {
    position: fixed;
    background: rgba(10,15,30,0.97);
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    line-height: 1.7;
    pointer-events: none;
    z-index: 100;
    max-width: 280px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.6);
    display: none;
}
.cy-tooltip.visible { display: block; }
.tt-title { font-weight: 700; color: #f1f5f9; margin-bottom: 4px; font-size: 13px; }
.tt-row   { color: #94a3b8; }
.tt-val   { color: #e2e8f0; }

.zoom-controls {
    position: fixed; left: 18px; bottom: 18px;
    display: flex; flex-direction: column; gap: 6px;
    z-index: 20;
}

.zoom-btn {
    width: 36px; height: 36px;
    background: rgba(15,23,42,0.93);
    border: 1px solid #334155;
    border-radius: 8px;
    color: #e5e7eb; font-size: 20px;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    backdrop-filter: blur(8px);
    transition: background 0.15s;
    user-select: none;
}
.zoom-btn:hover { background: #1e293b; }

.search-box {
    position: fixed; left: 18px; top: 72px;
    z-index: 20;
    display: flex; gap: 6px;
}
.search-input {
    background: rgba(15,23,42,0.93);
    border: 1px solid #334155;
    border-radius: 8px;
    color: #e5e7eb;
    font-size: 12px;
    padding: 6px 12px;
    width: 180px;
    outline: none;
    backdrop-filter: blur(8px);
}
.search-input::placeholder { color: #475569; }
.search-input:focus { border-color: #6366f1; }
</style>
</head>

<body>
<div class="header">
  <div class="header-left">
    <div class="title">&#x1F9E0; VisualTrick Architecture</div>
    <div class="subtitle">Deep Static Analysis &middot; Top-Down Repository Tree</div>
  </div>
  <div class="header-stats" id="headerStats">
    STATS_PLACEHOLDER
  </div>
</div>

<div id="cy"></div>

<div class="search-box">
  <input class="search-input" id="searchInput" placeholder="Search nodes..." />
</div>

<div class="zoom-controls">
  <button class="zoom-btn" id="zoomIn">+</button>
  <button class="zoom-btn" id="zoomOut">&#x2212;</button>
  <button class="zoom-btn" id="zoomReset">&#x2299;</button>
</div>

<button class="hamburger-btn" id="hamburgerBtn" title="Toggle Legend">
  <span class="ham-bar"></span>
  <span class="ham-bar"></span>
  <span class="ham-bar"></span>
</button>

<div class="legend-panel" id="legendPanel">
  <div class="legend-section-title">Nodes</div>
  <span class="legend-dot" style="background:#f59e0b;"></span> Project Root<br>
  <span class="legend-dot" style="background:#64748b;"></span> Folder<br>
  <span class="legend-dot" style="background:#3b82f6;"></span> Python File<br>
  <span class="legend-dot" style="background:#fbbf24;"></span> Function / Method<br>
  <span class="legend-dot" style="background:#818cf8;"></span> Class<br>
  <span class="legend-dot" style="background:#a78bfa;"></span> Internal Import<br>
  <span class="legend-dot" style="background:#10b981;"></span> External Import<br>
  <span class="legend-dot" style="background:#ef4444;"></span> API Route<br>
  <div class="legend-gap"></div>
  <div class="legend-section-title">Edges</div>
  <span class="legend-line" style="background:#d97706;"></span> Structural<br>
  <span class="legend-line" style="background:#6d28d9;"></span> Import<br>
  <span class="legend-line" style="background:#991b1b;"></span> Route<br>
  <span class="legend-line"
        style="background: repeating-linear-gradient(90deg,#f0abfc 0,#f0abfc 8px,transparent 8px,transparent 13px);"></span> Back-edge (cycle)
</div>

<div class="cy-tooltip" id="cyTooltip"></div>

<script>
const rawElements = ELEMENTS_PLACEHOLDER;

document.addEventListener('DOMContentLoaded', () => {
  const btn   = document.getElementById('hamburgerBtn');
  const panel = document.getElementById('legendPanel');
  btn.addEventListener('click', () => {
    const isOpen = panel.classList.toggle('open');
    btn.classList.toggle('open', isOpen);
  });
  document.addEventListener('click', (e) => {
    if (!btn.contains(e.target) && !panel.contains(e.target)) {
      panel.classList.remove('open');
      btn.classList.remove('open');
    }
  });
});

function detectBackEdges(elements) {
  const children = {};
  elements.forEach(el => {
    if (el.data && el.data.source && el.data.target) {
      if (!children[el.data.source]) children[el.data.source] = [];
      children[el.data.source].push(el.data.target);
    }
  });
  const visited = new Set(), inStack = new Set(), backKeys = new Set();
  function dfs(node) {
    visited.add(node); inStack.add(node);
    for (const nb of (children[node] || [])) {
      if (!visited.has(nb)) dfs(nb);
      else if (inStack.has(nb)) backKeys.add(node + '->' + nb);
    }
    inStack.delete(node);
  }
  const hasIncoming = new Set(
    elements.filter(e => e.data && e.data.source).map(e => e.data.target)
  );
  elements
    .filter(e => e.data && e.data.id && !hasIncoming.has(e.data.id))
    .forEach(e => { if (!visited.has(e.data.id)) dfs(e.data.id); });
  elements.forEach(el => {
    if (el.data && el.data.source && el.data.target)
      if (backKeys.has(el.data.source + '->' + el.data.target))
        el.data.isBackEdge = true;
  });
  return elements;
}

function getScale() {
  const vh = window.innerHeight - 58;
  return Math.max(0.35, Math.min(1.6, vh / 900));
}

function measureText(text, fontSize) {
  const canvas = document.createElement('canvas');
  const ctx    = canvas.getContext('2d');
  ctx.font     = '600 ' + fontSize + 'px Inter, system-ui, Arial';
  const words  = (text || '').replace(/[\u{1F4C1}\u{1F4C2}\u26A1\u{1F537}\u{1F6AB}\u{1F4CB}\u{1F310}\u{1F3A8}\u{1F40D}]/gu, '').trim().split(/[._\-\/\s]/);
  const longest = words.reduce((a, b) => a.length > b.length ? a : b, '');
  return ctx.measureText(longest).width;
}

const BASE = {
  root:            { fontSize: 14, minSize: 110, pad: 34 },
  folder:          { fontSize: 12, minSize:  96, pad: 28 },
  file:            { fontSize: 12, minSize:  96, pad: 30 },
  function:        { fontSize: 10, minSize:  64, pad: 20 },
  class:           { fontSize: 11, minSize:  72, pad: 22 },
  internal_import: { fontSize: 11, minSize:  78, pad: 24 },
  external_import: { fontSize: 11, minSize:  78, pad: 24 },
  route:           { fontSize: 10, minSize:  78, pad: 22 },
};

function buildElements(scale) {
  let els = JSON.parse(JSON.stringify(rawElements));
  els = detectBackEdges(els);
  els.forEach(el => {
    if (!el.data || !el.data.type || el.data.target !== undefined) return;
    const cfg = BASE[el.data.type];
    if (!cfg) return;
    const fs   = cfg.fontSize * scale;
    const pad  = cfg.pad      * scale;
    const minS = cfg.minSize  * scale;
    const tw   = measureText(el.data.label || '', fs);
    el.data.size     = Math.max(minS, tw + pad * 2);
    el.data.fontSize = fs;
  });
  return els;
}

let cy = null;

function buildLayout(scale) {
  return {
    name: 'dagre',
    rankDir: 'TB',
    ranker: 'tight-tree',
    align: 'DR',
    nodeSep:  Math.round(38  * scale),
    rankSep:  Math.round(180 * scale),
    edgeSep:  Math.round(8   * scale),
    padding:  Math.round(80  * scale),
    animate: true,
    animationDuration: 750,
    animationEasing: 'ease-in-out-cubic',
    nodeDimensionsIncludeLabels: true,
  };
}

function buildStyle(scale) {
  const bw = (n) => Math.max(1, n * scale);
  return [
    { selector: 'node[type="root"]', style: {
        shape: 'ellipse',
        'background-fill': 'linear-gradient',
        'background-gradient-stop-colors': '#fbbf24 #b45309',
        'background-gradient-direction': 'to-bottom',
        label: 'data(label)',
        'font-size': (BASE.root.fontSize * scale) + 'px',
        'font-weight': '700', color: '#fff',
        'text-valign': 'center', 'text-halign': 'center',
        'text-wrap': 'wrap', 'text-max-width': 'data(size)',
        width: 'data(size)', height: 'data(size)',
        'border-width': bw(3), 'border-color': '#fde68a',
    }},
    { selector: 'node[type="folder"]', style: {
        shape: 'ellipse',
        'background-fill': 'linear-gradient',
        'background-gradient-stop-colors': '#94a3b8 #1e293b',
        'background-gradient-direction': 'to-bottom',
        label: 'data(label)',
        'font-size': (BASE.folder.fontSize * scale) + 'px',
        'font-weight': '600', color: '#f1f5f9',
        'text-valign': 'center', 'text-halign': 'center',
        'text-wrap': 'wrap', 'text-max-width': 'data(size)',
        width: 'data(size)', height: 'data(size)',
        'border-width': bw(2), 'border-color': '#64748b',
    }},
    { selector: 'node[type="file"]', style: {
        shape: 'ellipse',
        'background-fill': 'linear-gradient',
        'background-gradient-stop-colors': '#60a5fa #1e3a8a',
        'background-gradient-direction': 'to-bottom',
        label: 'data(label)',
        'font-size': (BASE.file.fontSize * scale) + 'px',
        'font-weight': '600', color: '#e2e8f0',
        'text-valign': 'center', 'text-halign': 'center',
        'text-wrap': 'wrap', 'text-max-width': 'data(size)',
        width: 'data(size)', height: 'data(size)',
        'border-width': bw(2), 'border-color': '#93c5fd',
    }},
    { selector: 'node[type="function"]', style: {
        shape: 'ellipse',
        'background-fill': 'linear-gradient',
        'background-gradient-stop-colors': '#fde68a #d97706',
        'background-gradient-direction': 'to-bottom',
        label: 'data(label)',
        'font-size': (BASE.function.fontSize * scale) + 'px',
        'font-weight': '500', color: '#1c1917',
        'text-valign': 'center', 'text-halign': 'center',
        'text-wrap': 'wrap', 'text-max-width': 'data(size)',
        width: 'data(size)', height: 'data(size)',
        'border-width': bw(1.5), 'border-color': '#fbbf24',
    }},
    { selector: 'node[type="class"]', style: {
        shape: 'ellipse',
        'background-fill': 'linear-gradient',
        'background-gradient-stop-colors': '#818cf8 #3730a3',
        'background-gradient-direction': 'to-bottom',
        label: 'data(label)',
        'font-size': (BASE.class.fontSize * scale) + 'px',
        'font-weight': '600', color: '#e0e7ff',
        'text-valign': 'center', 'text-halign': 'center',
        'text-wrap': 'wrap', 'text-max-width': 'data(size)',
        width: 'data(size)', height: 'data(size)',
        'border-width': bw(2), 'border-color': '#a5b4fc',
    }},
    { selector: 'node[type="internal_import"]', style: {
        shape: 'ellipse',
        'background-fill': 'linear-gradient',
        'background-gradient-stop-colors': '#c4b5fd #5b21b6',
        'background-gradient-direction': 'to-bottom',
        label: 'data(label)',
        'font-size': (BASE.internal_import.fontSize * scale) + 'px',
        'font-weight': '500', color: '#ede9fe',
        'text-valign': 'center', 'text-halign': 'center',
        'text-wrap': 'wrap', 'text-max-width': 'data(size)',
        width: 'data(size)', height: 'data(size)',
        'border-width': bw(1.5), 'border-color': '#a78bfa',
    }},
    { selector: 'node[type="external_import"]', style: {
        shape: 'ellipse',
        'background-fill': 'linear-gradient',
        'background-gradient-stop-colors': '#34d399 #064e3b',
        'background-gradient-direction': 'to-bottom',
        label: 'data(label)',
        'font-size': (BASE.external_import.fontSize * scale) + 'px',
        'font-weight': '500', color: '#d1fae5',
        'text-valign': 'center', 'text-halign': 'center',
        'text-wrap': 'wrap', 'text-max-width': 'data(size)',
        width: 'data(size)', height: 'data(size)',
        'border-width': bw(1.5), 'border-color': '#6ee7b7',
    }},
    { selector: 'node[type="route"]', style: {
        shape: 'ellipse',
        'background-fill': 'linear-gradient',
        'background-gradient-stop-colors': '#f87171 #7f1d1d',
        'background-gradient-direction': 'to-bottom',
        label: 'data(label)',
        'font-size': (BASE.route.fontSize * scale) + 'px',
        'font-weight': '600', color: '#fff',
        'text-valign': 'center', 'text-halign': 'center',
        'text-wrap': 'wrap', 'text-max-width': 'data(size)',
        width: 'data(size)', height: 'data(size)',
        'border-width': bw(2), 'border-color': '#fca5a5',
    }},
    { selector: 'edge[type="root-folder"]', style: { width: bw(2.2), 'line-color': '#d97706', 'target-arrow-color': '#fbbf24', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', opacity: 0.85 }},
    { selector: 'edge[type="folder-file"]', style: { width: bw(1.8), 'line-color': '#475569', 'target-arrow-color': '#94a3b8', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', opacity: 0.8 }},
    { selector: 'edge[type="root-file"]',   style: { width: bw(1.8), 'line-color': '#92400e', 'target-arrow-color': '#fbbf24', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', opacity: 0.8 }},
    { selector: 'edge[type="file-function"]', style: { width: bw(1.4), 'line-color': '#92400e', 'target-arrow-color': '#fde68a', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', opacity: 0.75 }},
    { selector: 'edge[type="file-class"]',    style: { width: bw(1.5), 'line-color': '#3730a3', 'target-arrow-color': '#a5b4fc', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', opacity: 0.8 }},
    { selector: 'edge[type="class-method"]',  style: { width: bw(1.2), 'line-color': '#4338ca', 'target-arrow-color': '#818cf8', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', opacity: 0.7 }},
    { selector: 'edge[type="file-internal"]', style: { width: bw(1.5), 'line-color': '#6d28d9', 'target-arrow-color': '#c4b5fd', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', opacity: 0.8 }},
    { selector: 'edge[type="file-external"]', style: { width: bw(1.5), 'line-color': '#1e40af', 'target-arrow-color': '#93c5fd', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', opacity: 0.8 }},
    { selector: 'edge[type="file-route"]',    style: { width: bw(1.5), 'line-color': '#991b1b', 'target-arrow-color': '#fca5a5', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', opacity: 0.8 }},
    { selector: 'edge[type="cross-call"]',    style: { width: bw(1.3), 'line-color': '#0891b2', 'target-arrow-color': '#67e8f9', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', opacity: 0.7, 'line-style': 'dashed', 'line-dash-pattern': [5, 4] }},
    { selector: 'edge[?isBackEdge]', style: {
        width: bw(2), 'line-color': '#f0abfc', 'line-style': 'dashed', 'line-dash-pattern': [8, 5],
        'target-arrow-color': '#f0abfc', 'target-arrow-shape': 'triangle',
        'source-arrow-color': '#f0abfc', 'source-arrow-shape': 'circle',
        'curve-style': 'unbundled-bezier', 'control-point-distances': [80],
        'control-point-weights': [0.5], opacity: 0.9, 'z-index': 999,
    }},
    { selector: '.faded',        style: { opacity: 0.07 }},
    { selector: '.highlighted',  style: { opacity: 1    }},
    { selector: 'node:selected', style: { 'border-width': bw(4), 'border-color': '#facc15' }},
    { selector: '.search-match', style: { 'border-width': bw(4), 'border-color': '#facc15', opacity: 1 }},
    { selector: '.search-dim',   style: { opacity: 0.12 }},
  ];
}

function initCy() {
  const scale    = getScale();
  const elements = buildElements(scale);

  if (cy) { cy.destroy(); cy = null; }

  cy = cytoscape({
    container: document.getElementById('cy'),
    elements,
    style: buildStyle(scale),
    layout: buildLayout(scale),
  });

  cy.minZoom(0.04);
  cy.maxZoom(5.0);

  cy.one('layoutstop', () => { cy.fit(undefined, Math.round(60 * scale)); cy.center(); });

  document.getElementById('zoomIn').onclick    = () => cy.zoom({ level: cy.zoom() * 1.25, renderedPosition: { x: cy.width()/2, y: cy.height()/2 }});
  document.getElementById('zoomOut').onclick   = () => cy.zoom({ level: cy.zoom() * 0.8,  renderedPosition: { x: cy.width()/2, y: cy.height()/2 }});
  document.getElementById('zoomReset').onclick = () => { cy.fit(undefined, Math.round(60 * scale)); cy.center(); };

  cy.on('mouseover', 'node', e => {
    cy.elements().addClass('faded');
    e.target.closedNeighborhood().removeClass('faded').addClass('highlighted');
  });
  cy.on('mouseout', 'node', () => cy.elements().removeClass('faded highlighted'));

  const tooltip = document.getElementById('cyTooltip');
  cy.on('mouseover', 'node', e => {
    const d = e.target.data();
    if (!d.meta) return;
    const m = d.meta;
    let rows = '<div class="tt-title">' + (d.label || d.id) + '</div>';
    if (m.type)        rows += '<span class="tt-row">Type: </span><span class="tt-val">' + m.type + '</span><br>';
    if (m.lines)       rows += '<span class="tt-row">Lines: </span><span class="tt-val">' + m.lines + '</span><br>';
    if (m.complexity !== undefined) rows += '<span class="tt-row">Complexity: </span><span class="tt-val">' + m.complexity + '</span><br>';
    if (m.args)        rows += '<span class="tt-row">Args: </span><span class="tt-val">' + m.args + '</span><br>';
    if (m.returns)     rows += '<span class="tt-row">Returns: </span><span class="tt-val">' + m.returns + '</span><br>';
    if (m.decorators && m.decorators.length) rows += '<span class="tt-row">Decorators: </span><span class="tt-val">' + m.decorators.join(', ') + '</span><br>';
    if (m.bases && m.bases.length) rows += '<span class="tt-row">Inherits: </span><span class="tt-val">' + m.bases.join(', ') + '</span><br>';
    if (m.docstring)   rows += '<span class="tt-row">Doc: </span><span class="tt-val">' + m.docstring.slice(0, 80) + (m.docstring.length > 80 ? '...' : '') + '</span><br>';
    if (m.async)       rows += '<span class="tt-val" style="color:#34d399;">async</span><br>';
    tooltip.innerHTML = rows;
    tooltip.classList.add('visible');
  });
  cy.on('mousemove', e => {
    tooltip.style.left = (e.originalEvent.clientX + 14) + 'px';
    tooltip.style.top  = (e.originalEvent.clientY + 14) + 'px';
  });
  cy.on('mouseout', 'node', () => tooltip.classList.remove('visible'));

  const searchInput = document.getElementById('searchInput');
  searchInput.addEventListener('input', () => {
    const q = searchInput.value.trim().toLowerCase();
    cy.elements().removeClass('search-match search-dim');
    if (!q) return;
    const matches = cy.nodes().filter(n =>
      (n.data('label') || '').toLowerCase().includes(q) ||
      (n.data('id')    || '').toLowerCase().includes(q)
    );
    if (matches.length === 0) return;
    cy.nodes().addClass('search-dim');
    matches.removeClass('search-dim').addClass('search-match');
  });
}

let resizeTimer = null;
window.addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(initCy, 250); });
window.addEventListener('DOMContentLoaded', initCy);
</script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Deep AST analysis helpers
# ─────────────────────────────────────────────────────────────────────────────

STDLIB_MODULES = {
    "os", "sys", "re", "json", "math", "time", "datetime", "pathlib",
    "subprocess", "threading", "multiprocessing", "collections", "itertools",
    "functools", "typing", "io", "abc", "copy", "random", "hashlib",
    "logging", "unittest", "argparse", "shutil", "tempfile", "glob",
    "socket", "http", "urllib", "email", "html", "xml", "csv", "sqlite3",
    "asyncio", "contextlib", "dataclasses", "enum", "struct", "traceback",
    "warnings", "weakref", "inspect", "ast", "dis", "gc", "platform",
    "signal", "stat", "string", "textwrap", "uuid", "base64", "binascii",
    "pprint", "queue", "heapq", "bisect", "array", "decimal", "fractions",
    "statistics", "operator", "pickle", "shelve", "zipfile", "tarfile",
}


def _cyclomatic_complexity(func_node: ast.AST) -> int:
    count = 1
    for node in ast.walk(func_node):
        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                              ast.With, ast.Assert, ast.comprehension)):
            count += 1
        elif isinstance(node, ast.BoolOp):
            count += len(node.values) - 1
    return count


def _get_decorator_names(decorators: list) -> list:
    names = []
    for d in decorators:
        if isinstance(d, ast.Name):
            names.append(d.id)
        elif isinstance(d, ast.Attribute):
            names.append(_unparse_attr(d))
        elif isinstance(d, ast.Call):
            if isinstance(d.func, ast.Name):
                names.append(d.func.id)
            elif isinstance(d.func, ast.Attribute):
                names.append(_unparse_attr(d.func))
    return names


def _unparse_attr(node: ast.Attribute) -> str:
    parts = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
    return ".".join(reversed(parts))


def _annotation_str(ann) -> str:
    if ann is None:
        return ""
    try:
        return ast.unparse(ann)
    except Exception:
        return "?"


def _docstring(node: ast.AST) -> str:
    try:
        s = ast.get_docstring(node)
        return s if s else ""
    except Exception:
        return ""


def _extract_calls(func_node: ast.AST) -> list:
    calls = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    return list(set(calls))


def deep_analyze_file(file_path: str, internal_modules: set) -> dict:
    result = {
        "imports": [],
        "functions": [],
        "classes": [],
        "routes": [],
        "calls": [],
        "lines": 0,
        "has_main": False,
        "docstring": "",
    }

    try:
        source = open(file_path, "r", encoding="utf-8", errors="ignore").read()
    except Exception:
        return result

    result["lines"] = source.count("\n") + 1

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        result["imports"] = re.findall(r"^\s*(?:import|from)\s+([\w]+)", source, re.MULTILINE)
        return result

    result["docstring"] = _docstring(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result["imports"].append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                result["imports"].append(node.module.split(".")[0])

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in node.args.args]
            decorators = _get_decorator_names(node.decorator_list)
            func_info = {
                "name": node.name,
                "args": args,
                "returns": _annotation_str(node.returns),
                "decorators": decorators,
                "async": isinstance(node, ast.AsyncFunctionDef),
                "complexity": _cyclomatic_complexity(node),
                "lines": (node.end_lineno - node.lineno + 1) if hasattr(node, "end_lineno") else 0,
                "docstring": _docstring(node),
                "calls": _extract_calls(node),
            }
            result["functions"].append(func_info)

            for d in node.decorator_list:
                route = _try_extract_route(d, node.name)
                if route:
                    result["routes"].append(route)

        elif isinstance(node, ast.ClassDef):
            bases = []
            for b in node.bases:
                if isinstance(b, ast.Name):
                    bases.append(b.id)
                elif isinstance(b, ast.Attribute):
                    bases.append(_unparse_attr(b))

            methods = []
            for item in ast.iter_child_nodes(node):
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = [a.arg for a in item.args.args if a.arg != "self"]
                    method_info = {
                        "name": item.name,
                        "args": args,
                        "returns": _annotation_str(item.returns),
                        "decorators": _get_decorator_names(item.decorator_list),
                        "async": isinstance(item, ast.AsyncFunctionDef),
                        "complexity": _cyclomatic_complexity(item),
                        "lines": (item.end_lineno - item.lineno + 1) if hasattr(item, "end_lineno") else 0,
                        "docstring": _docstring(item),
                    }
                    methods.append(method_info)

                    for d in item.decorator_list:
                        route = _try_extract_route(d, item.name)
                        if route:
                            result["routes"].append(route)

            cls_decorators = _get_decorator_names(node.decorator_list)
            result["classes"].append({
                "name": node.name,
                "bases": bases,
                "decorators": cls_decorators,
                "methods": methods,
                "lines": (node.end_lineno - node.lineno + 1) if hasattr(node, "end_lineno") else 0,
                "docstring": _docstring(node),
            })

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                result["calls"].append(node.value.func.id)
        if isinstance(node, ast.If):
            test = node.test
            if (isinstance(test, ast.Compare)
                    and isinstance(test.left, ast.Name)
                    and test.left.id == "__name__"):
                result["has_main"] = True

    return result


def _try_extract_route(decorator_node, func_name: str):
    methods_map = {
        "get": "GET", "post": "POST", "put": "PUT", "delete": "DELETE",
        "patch": "PATCH", "head": "HEAD", "options": "OPTIONS",
        "route": "ANY",
    }
    if not isinstance(decorator_node, ast.Call):
        return None
    func = decorator_node.func
    method = None
    if isinstance(func, ast.Attribute):
        method = methods_map.get(func.attr.lower())
    if method is None:
        return None
    if decorator_node.args and isinstance(decorator_node.args[0], ast.Constant):
        path = str(decorator_node.args[0].value)
        return {"method": method, "path": path, "function": func_name}
    return None


def scan_repository(target_path: str) -> dict:
    py_files = []
    for root, dirs, files in os.walk(target_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")
                   and d not in {"__pycache__", "node_modules", ".git",
                                 "venv", ".venv", "env", "dist", "build", ".mypy_cache"}]
        for fname in files:
            if fname.endswith(".py"):
                py_files.append(os.path.join(root, fname))

    internal_modules = set()
    for fp in py_files:
        name = os.path.splitext(os.path.basename(fp))[0]
        internal_modules.add(name)
        folder = os.path.basename(os.path.dirname(fp))
        if folder:
            internal_modules.add(folder)

    file_analyses: dict = {}
    for fp in py_files:
        file_analyses[fp] = deep_analyze_file(fp, internal_modules)

    all_imports: dict = {fp: a["imports"] for fp, a in file_analyses.items()}
    all_functions: dict = {fp: a["functions"] for fp, a in file_analyses.items()}
    all_classes: dict = {fp: a["classes"] for fp, a in file_analyses.items()}
    all_routes: list = []
    for a in file_analyses.values():
        all_routes.extend(a["routes"])

    func_defined_in: dict = {}
    for fp, funcs in all_functions.items():
        for f in funcs:
            if isinstance(f, dict):
                func_defined_in[f["name"]] = fp
    for fp, classes in all_classes.items():
        for cls in classes:
            if isinstance(cls, dict):
                for m in cls.get("methods", []):
                    if isinstance(m, dict):
                        func_defined_in[m["name"]] = fp

    cross_calls: list = []
    for fp, funcs in all_functions.items():
        for f in funcs:
            if not isinstance(f, dict):
                continue
            for called in f.get("calls", []):
                target_fp = func_defined_in.get(called)
                if target_fp and target_fp != fp:
                    cross_calls.append((fp, target_fp))

    internal_count = 0
    external_count = 0
    for imps in all_imports.values():
        for imp in imps:
            root_mod = imp.split(".")[0]
            if root_mod in internal_modules:
                internal_count += 1
            elif root_mod not in STDLIB_MODULES:
                external_count += 1

    requirements: list = []
    req_path = os.path.join(target_path, "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    requirements.append(line)

    non_py_files: dict = {
        "html": [], "css": [], "js": [], "ts": [], "react": [], "json": [],
    }
    for root, dirs, files in os.walk(target_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")
                   and d not in {"__pycache__", "node_modules", ".git",
                                 "venv", ".venv", "env", "dist", "build"}]
        for fname in files:
            fl = fname.lower()
            if fl.endswith(".html"):
                non_py_files["html"].append(os.path.join(root, fname))
            elif fl.endswith(".css"):
                non_py_files["css"].append(os.path.join(root, fname))
            elif fl.endswith(".js"):
                non_py_files["js"].append(os.path.join(root, fname))
            elif fl.endswith(".ts") and not fl.endswith(".d.ts"):
                non_py_files["ts"].append(os.path.join(root, fname))
            elif fl.endswith(".tsx") or fl.endswith(".jsx"):
                non_py_files["react"].append(os.path.join(root, fname))
            elif fl.endswith(".json"):
                non_py_files["json"].append(os.path.join(root, fname))

    all_files = (
        [os.path.relpath(f, target_path) for f in py_files]
        + [os.path.relpath(f, target_path) for lst in non_py_files.values() for f in lst]
    )

    return {
        "files": all_files,
        "py_files": py_files,
        "imports": all_imports,
        "functions": all_functions,
        "classes": all_classes,
        "routes": all_routes,
        "cross_calls": cross_calls,
        "requirements": requirements,
        "internal_modules": internal_modules,
        "import_stats": {"internal": internal_count, "external": external_count},
        "non_py_files": non_py_files,
        "file_analyses": file_analyses,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Graph builder
# ─────────────────────────────────────────────────────────────────────────────

def build_graph(repo_data, target_path: str):
    nodes          = []
    edges          = []
    seen           = set()
    folder_nodes   = {}

    # ── NEW: track edges already added to prevent duplicates ──────────────────
    seen_edges: set = set()

    def add_edge(source: str, target: str, edge_type: str):
        """Add an edge only if this exact (source, target, type) hasn't been added."""
        key = f"{source}||{target}||{edge_type}"
        if key not in seen_edges:
            seen_edges.add(key)
            edges.append({"data": {"source": source, "target": target, "type": edge_type}})
    # ──────────────────────────────────────────────────────────────────────────

    internal_modules = repo_data.get("internal_modules", set())
    stats            = repo_data.get("import_stats", {})
    internal_count   = stats.get("internal", 0)
    external_count   = stats.get("external", 0)
    file_count       = len(repo_data.get("py_files", repo_data.get("imports", {})))
    route_count      = len(repo_data.get("routes", []))
    func_count       = sum(len(v) for v in repo_data.get("functions", {}).values())
    class_count      = sum(len(v) for v in repo_data.get("classes", {}).values())

    file_analyses    = repo_data.get("file_analyses", {})

    root_id = os.path.basename(os.path.abspath(target_path)) or "project"
    nodes.append({"data": {
        "id": root_id,
        "label": root_id,
        "type": "root",
        "meta": {"type": "Project Root"},
    }})
    seen.add(root_id)

    def add_node_once(node_id, node_data):
        if node_id not in seen:
            nodes.append(node_data)
            seen.add(node_id)

    for file_path, imports in repo_data["imports"].items():
        fname     = os.path.basename(file_path)
        rel       = os.path.relpath(file_path, target_path)
        parts     = rel.replace("\\", "/").split("/")

        # ── FIX: files directly in the project root (parts == [filename]) ──
        # Previously this created a spurious "folder::root" intermediate node,
        # which produced two arrows (root→folder::root→file) instead of one.
        # Now we connect such files directly to root_id with "root-file" edge.
        is_root_level = len(parts) == 1
        folder        = parts[-2] if not is_root_level else None
        folder_id     = f"folder::{folder}" if folder else None

        analysis = file_analyses.get(file_path, {})

        if not is_root_level:
            # File lives inside a subdirectory — use the folder intermediate node
            if folder not in folder_nodes:
                folder_nodes[folder] = True
                add_node_once(folder_id, {"data": {
                    "id": folder_id,
                    "label": folder,
                    "type": "folder",
                    "meta": {"type": "Folder"},
                }})
                add_edge(root_id, folder_id, "root-folder")

            add_node_once(fname, {"data": {
                "id": fname,
                "label": fname,
                "type": "file",
                "weight": max(1, len(imports)),
                "meta": {
                    "type": "Python File",
                    "lines": analysis.get("lines", "?"),
                    "docstring": analysis.get("docstring", ""),
                    "has_main": analysis.get("has_main", False),
                },
            }})
            add_edge(folder_id, fname, "folder-file")

        else:
            # File is directly under the project root — connect straight to root
            add_node_once(fname, {"data": {
                "id": fname,
                "label": fname,
                "type": "file",
                "weight": max(1, len(imports)),
                "meta": {
                    "type": "Python File",
                    "lines": analysis.get("lines", "?"),
                    "docstring": analysis.get("docstring", ""),
                    "has_main": analysis.get("has_main", False),
                },
            }})
            add_edge(root_id, fname, "root-file")

        for imp in set(imports):
            imp_id    = imp.split(".")[0]
            if not imp_id:
                continue
            node_type = "internal_import" if imp_id in internal_modules else "external_import"
            edge_type = "file-internal"   if imp_id in internal_modules else "file-external"
            if node_type == "external_import" and imp_id in STDLIB_MODULES:
                continue
            add_node_once(imp_id, {"data": {
                "id": imp_id, "label": imp_id, "type": node_type, "weight": 1,
                "meta": {"type": node_type.replace("_", " ").title()},
            }})
            add_edge(fname, imp_id, edge_type)

    for file_path, classes in repo_data.get("classes", {}).items():
        fname = os.path.basename(file_path)
        for cls in classes:
            if not isinstance(cls, dict):
                continue
            cls_id = f"cls::{fname}::{cls['name']}"
            add_node_once(cls_id, {"data": {
                "id": cls_id,
                "label": cls["name"],
                "type": "class",
                "meta": {
                    "type": "Class",
                    "lines": cls.get("lines", "?"),
                    "bases": cls.get("bases", []),
                    "decorators": cls.get("decorators", []),
                    "docstring": cls.get("docstring", ""),
                },
            }})
            add_edge(fname, cls_id, "file-class")

            for method in cls.get("methods", []):
                if not isinstance(method, dict):
                    continue
                m_id = f"method::{fname}::{cls['name']}::{method['name']}"
                add_node_once(m_id, {"data": {
                    "id": m_id,
                    "label": method["name"],
                    "type": "function",
                    "meta": {
                        "type": "Method",
                        "args": ", ".join(method.get("args", [])),
                        "returns": method.get("returns", ""),
                        "decorators": method.get("decorators", []),
                        "async": method.get("async", False),
                        "complexity": method.get("complexity", 1),
                        "lines": method.get("lines", "?"),
                        "docstring": method.get("docstring", ""),
                    },
                }})
                add_edge(cls_id, m_id, "class-method")

    for file_path, funcs in repo_data.get("functions", {}).items():
        fname = os.path.basename(file_path)
        for func in funcs:
            if isinstance(func, str):
                func_name = func
                func_meta = {
                    "type": "Function",
                    "args": "",
                    "returns": "",
                    "decorators": [],
                    "async": False,
                    "complexity": 1,
                    "lines": "?",
                    "docstring": "",
                }
            elif isinstance(func, dict):
                func_name = func["name"]
                func_meta = {
                    "type": "Function",
                    "args": ", ".join(func.get("args", [])),
                    "returns": func.get("returns", ""),
                    "decorators": func.get("decorators", []),
                    "async": func.get("async", False),
                    "complexity": func.get("complexity", 1),
                    "lines": func.get("lines", "?"),
                    "docstring": func.get("docstring", ""),
                }
            else:
                continue

            func_id = f"func::{fname}::{func_name}"
            add_node_once(func_id, {"data": {
                "id": func_id,
                "label": func_name,
                "type": "function",
                "meta": func_meta,
            }})
            add_edge(fname, func_id, "file-function")

    seen_cross = set()
    for caller_fp, callee_fp in repo_data.get("cross_calls", []):
        caller_fname = os.path.basename(caller_fp)
        callee_fname = os.path.basename(callee_fp)
        key = f"{caller_fname}=>{callee_fname}"
        if key not in seen_cross and caller_fname != callee_fname:
            seen_cross.add(key)
            add_edge(caller_fname, callee_fname, "cross-call")

    for route in repo_data.get("routes", []):
        route_id  = f"route::{route['method']}::{route['path']}"
        func_name = route.get("function", "")
        add_node_once(route_id, {"data": {
            "id": route_id,
            "label": f"{route['method']} {route['path']}",
            "type": "route",
            "meta": {"type": "API Route", "method": route["method"], "path": route["path"]},
        }})
        if func_name:
            for file_path, funcs in repo_data.get("functions", {}).items():
                for f in funcs:
                    f_name = f if isinstance(f, str) else (f.get("name") if isinstance(f, dict) else None)
                    if f_name == func_name:
                        add_edge(os.path.basename(file_path), route_id, "file-route")
                        break
            for file_path, classes in repo_data.get("classes", {}).items():
                for cls in classes:
                    if not isinstance(cls, dict):
                        continue
                    for m in cls.get("methods", []):
                        if not isinstance(m, dict):
                            continue
                        if m["name"] == func_name:
                            add_edge(os.path.basename(file_path), route_id, "file-route")

    def pill(color, label):
        return (
            f'<div class="stat-pill">'
            f'<span class="stat-dot" style="background:{color};"></span>{label}'
            f'</div>'
        )

    pills = [
        pill("#f59e0b", "1 Root"),
        pill("#64748b", f"{len(folder_nodes)} Folders"),
        pill("#3b82f6", f"{file_count} Files"),
        pill("#818cf8", f"{class_count} Classes"),
        pill("#fbbf24", f"{func_count} Functions"),
    ]
    if internal_count:
        pills.append(pill("#a78bfa", f"{internal_count} Internal"))
    if external_count:
        pills.append(pill("#10b981", f"{external_count} External"))
    if route_count:
        pills.append(pill("#ef4444", f"{route_count} Routes"))

    stats_html = "\n".join(pills)

    elements = nodes + edges
    html_out = HTML_TEMPLATE.replace("ELEMENTS_PLACEHOLDER", json.dumps(elements, indent=2))
    html_out = html_out.replace("STATS_PLACEHOLDER", stats_html)

    docs_dir = os.path.join(target_path, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    output_path = os.path.join(docs_dir, "architecture.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"Graph generated: {output_path}")
    return output_path