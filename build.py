"""Build index.html (a standalone GitHub Pages site) from the Clear Dead Stock design file.

usage: python3 build.py <path to Main.dc.html>

The design file is a Design-canvas component: an <x-dc> template with {{holes}}, <sc-if>/<sc-for>,
and a `class Component extends DCLogic` script. This script keeps that markup and logic as-is and
adds a ~100-line renderer (render.js inline) so the page runs anywhere. Asset URLs (/_blob/<id>)
are rewritten to local files copied into assets/.
"""
import json, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).parent
CAP = Path("/Users/pratik.agarwal/Documents/ROCE/prototypes/supplier-panel-clone/capture/assets")
BLOBS = {
    # product photos
    "5d01013230daf632080f4a86a39a9c57": "01f520c11cab.webp", "4cfe1fa3f1f067b7d6783fb7b6cbcdf9": "94ab68d18234.webp",
    "1842d9857cf04a20caa86f264d900d7f": "d237df44430b.webp", "1b9f75c78fa42ebaa3bab832f7401781": "745ab17f0815.webp",
    "b333e9fe9ba8e9b9d145cb138cde7c38": "de369e36af19.webp", "3136eab2acd1c963e0cf0e7aedde1176": "19e9bf429be9.webp",
    "1310a38e65714ebcf1f362fa22531650": "91de7786a229.webp", "42aeaaa9eb43faac213be137d8888f5a": "6f35aaf20eb3.webp",
    "360c3e2299ca771429bac23092648be7": "7450c3b9a245.webp", "a481fcd12ac8cdfcb499440e3d4e1606": "2986b2d4edfb.webp",
    "a72250f3f25b07ceea30b129cf9588fa": "013034852dfd.webp", "191e08b0f8ddedb0840dac3acc7270f8": "a9591dc9caf0.webp",
    "692173d62b01ca7bf2dde89b1a856b9a": "0255e2a87bb0.webp", "c83f1b8f768016ecd69eeb68e3501f39": "6d79909c15dd.webp",
    "a7e432b3126c487193352408af3965c6": "c23a92e5a955.webp", "a531daa1c7bb3a77c8421e55943f0dec": "775f210223a2.webp",
    "7c556c09a4ff750c1d59f67ea2f8d908": "1ee9b9644ac5.webp", "c02826054f367c51fa1ae1ae01123f4a": "7de3b2f0a42c.webp",
    # sidebar icons
    "49bd6d9df6cbcc56e31564fe14309b5b": "g6vmq8.svg", "5db94fbe1ba137b53571cc0a1b2d4bf7": "1d09b5i.svg",
    "e4db3c0a588f345250cd15dde8047410": "1e61u6d.svg", "cfd3660ad58ae9b7c6575eee6a0cb2ca": "19o6r7m.svg",
    "a5d2ad9187864b03abb47200c55d6d53": "22t6ug.svg", "72fc78037f1dfc73286ab0b347631590": "ge392q.svg",
    "8c7f1a66b7440c15b70bceaf106daa07": "byh1hx.svg", "010a2185e7c6b3078cc03690792aa908": "1ahl8d6.svg",
    "7602adbea6c89775dfa89d0275913665": "1x022kq.svg", "1f54829665efab952669568f9adffb2b": "1siaqm3.svg",
    "e7a520e16be582aa012d37830d65c829": "1dnxc99.svg", "15e951b2d072d7736a4ef1eaa89e875d": "rsiub6.svg",
    "a26a007419e2d5291915b2774d3f59e6": "v77nek.svg", "27decb648a9c1e633e4c41ccba358fe6": "yskyzy.svg",
    "335d1b2dc9df6901703d939d75a9654c": "u5cl7u.svg", "5163264d6b5e777c6410b49470340623": "19ow69v.svg",
    "e919e1522cf459d9516cae259fe03fe0": "1z0qqo8.svg", "212162306ec78ba4a3554235a4b780d8": "qn0nxa.svg",
    "42a2541c60ddab88f59ff99089732202": "1w8fsz0.svg", "cf3add19a269732f0eb4f6939bfa617a": "3drcb7.svg",
    "051f7e1a6c0d938f8a3df9c318636657": "1ri1zz5.svg", "390d5f15bc514b1b653f0c6f266368d5": "1o137fn.svg",
    "1304ebe47d230bb0d2a0a3a4bd7ce35c": "1iqruge.svg", "057fdcba6088ca245dfe0205119ac33f": "1lhrye9.svg",
    "dad81e73861f1423d2f6061fd443c139": "giba1m.svg", "617dc9f7eb76cc94a500827fbae23538": "1u13aur.svg",
    # Mier fonts
    "ecc2e5fa45043f7296c4057ade623af8": "Mier_B02-Book.woff2", "623207d2f04f8530789b0ce887b254f3": "Mier_B02-Demi.woff2",
    "e51b3841e15d2469d252b7b902f69793": "Mier_B02-Bold.woff2",
}

src = Path(sys.argv[1]).read_text()
(HERE / "assets").mkdir(exist_ok=True)
for bid, f in BLOBS.items():
    shutil.copy2((CAP / "prod" / f) if f.endswith(".webp") else (CAP / f), HERE / "assets" / f)
    src = src.replace("/_blob/" + bid, "assets/" + f)
left = re.findall(r"/_blob/[0-9a-f]+", src)
assert not left, f"unmapped assets: {set(left)}"

helmet = re.search(r"<helmet>(.*?)</helmet>", src, re.S).group(1)
body = re.search(r"</helmet>(.*)</x-dc>", src, re.S).group(1)
m = re.search(r"<script type=\"text/x-dc\" data-dc-script data-props='(.*?)'>(.*?)</script>", src, re.S)
props = json.loads(m.group(1).replace("&amp;", "&").replace("&#39;", "'"))
defaults = {k: v["default"] for k, v in props.items() if isinstance(v, dict) and "default" in v}
code = m.group(2)

# <sc-for> directly wrapping a <tr> would be foster-parented out of <tbody> by the HTML parser:
# move its list/as onto the <tr> itself.
body = re.sub(r'<sc-for list="([^"]+)" as="([^"]+)"[^>]*>\s*<tr', r'<tr data-for="\1" data-as="\2"', body)
body = re.sub(r"</tr>\s*</sc-for>", "</tr>", body)

runtime = r"""
<script>
(function(){
class DCLogic { constructor(props){ this.props = props; this.state = {}; }
  setState(p){ Object.assign(this.state, typeof p === 'function' ? p(this.state) : p); schedule(); } forceUpdate(){ schedule(); } }
window.DCLogic = DCLogic;
const HOLE = /\{\{\s*([^}]+?)\s*\}\}/g, WHOLE = /^\s*\{\{\s*([^}]+?)\s*\}\}\s*$/;
function look(scope, path){ path = path.trim();
  if (path === 'true') return true; if (path === 'false') return false; if (path === 'null') return null;
  if (/^-?\d+(\.\d+)?$/.test(path)) return Number(path);
  return path.split('.').reduce((o, k) => (o == null ? undefined : o[k]), scope); }
function interp(s, scope){ return s.replace(HOLE, (_, p) => { const v = look(scope, p); return v == null ? '' : String(v); }); }
const BOOL = new Set(['checked','disabled','selected','readonly']);
function render(node, scope){
  if (node.nodeType === 3) return [document.createTextNode(interp(node.nodeValue, scope))];
  if (node.nodeType !== 1) return [];
  const tag = node.tagName.toLowerCase();
  if (tag === 'sc-if') { const v = look(scope, (node.getAttribute('value').match(WHOLE)||[])[1]||'');
    return v ? kids(node, scope) : []; }
  const forAttr = tag === 'sc-for' ? node.getAttribute('list') : node.getAttribute('data-for');
  if (forAttr != null && !node.__inFor) { const list = look(scope, forAttr.match(WHOLE)[1]) || [];
    const as = tag === 'sc-for' ? node.getAttribute('as') : node.getAttribute('data-as'); const out = [];
    list.forEach((item, i) => { const s = Object.assign({}, scope, {[as]: item, $index: i});
      if (tag === 'sc-for') out.push(...kids(node, s)); else { node.__inFor = true; out.push(...render(node, s)); node.__inFor = false; } });
    return out; }
  const el = document.createElementNS(node.namespaceURI, node.localName);
  for (const a of Array.from(node.attributes)) { const n = a.name;
    if (n.startsWith('hint-') || n === 'data-for' || n === 'data-as') continue;
    const whole = a.value.match(WHOLE);
    if (n.startsWith('on')) { const fn = whole && look(scope, whole[1]); if (typeof fn === 'function') {
        const ev = n.slice(2); el.addEventListener(ev === 'change' && el.type !== 'checkbox' ? 'change' : ev, fn); } continue; }
    if (whole) { const v = look(scope, whole[1]);
      if (BOOL.has(n)) { if (v) el.setAttribute(n, ''); el[n] = !!v; continue; }
      if (n === 'value') { el.setAttribute('value', v == null ? '' : v); continue; }
      if (v == null || v === false) continue; el.setAttribute(n, String(v)); continue; }
    el.setAttribute(n, interp(a.value, scope)); }
  const src = tag === 'template' ? node.content : node;
  for (const c of Array.from(src.childNodes)) render(c, scope).forEach(k => el.appendChild(k));
  return [el]; }
function kids(node, scope){ const out = []; for (const c of Array.from(node.childNodes)) out.push(...render(c, scope)); return out; }
let comp, root, tpl, pending = false;
function draw(){ pending = false; const vals = comp.renderVals(); const frag = document.createDocumentFragment();
  for (const c of Array.from(tpl.content.childNodes)) render(c, vals).forEach(k => frag.appendChild(k));
  const y = window.scrollY; root.replaceChildren(frag); window.scrollTo(0, y); }
function schedule(){ if (!pending) { pending = true; setTimeout(draw, 0); } }
window.__mount = function(Component, props){ tpl = document.getElementById('tpl'); root = document.getElementById('root');
  comp = new Component(props); draw(); };
})();
</script>
"""

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Clear Dead Stock · Seller opt-in (mock)</title>
{helmet}
</head>
<body>
<div id="root"></div>
<template id="tpl">{body}</template>
{runtime}
<script>
{code}
window.__mount(Component, {json.dumps(defaults)});
</script>
</body>
</html>
"""
(HERE / "index.html").write_text(html)
print("wrote", HERE / "index.html", len(html), "bytes;", len(BLOBS), "assets")
