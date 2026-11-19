# export_demo.py - Tạo trang demo hoạt ảnh cho cả 5 thuật toán trên các mê cung sinh từ MSSV.
#
#   python export_demo.py                  # đọc mssv_list.txt, ghi demo/demo_thuat_toan.html
#   python export_demo.py --mssv A --mssv B --mssv C
#
# Trang HTML được tạo là một file độc lập (không cần mạng, không cần server).
# Mỗi lần thêm/sửa thuật toán hoặc đổi MSSV, chạy lại lệnh này để cập nhật demo.
# Dữ liệu trong trang là đường đi thật do chính code trong algorithms/ sinh ra.

import argparse
import json
import os

from maze_env import (MazeEnv, maze_size_from_mssv, seed_from_mssv,
                      generate_maze, shortest_path_length)
from run_experiments import ALGORITHMS, read_mssv_file
import importlib


def run_trace(fn, maze, start, goal, limit):
    env = MazeEnv(maze, start, goal)
    mem = {}
    path = [list(env.pos)]
    hlog = []  # LRTA*: [bước, hàng, cột, H mới của ô đang đứng]
    moves = 0
    while env.pos != goal and moves < limit:
        pos = env.pos
        action, mem = fn(pos, goal, env.view(), mem)
        if isinstance(mem.get("H"), dict) and pos in mem["H"]:
            hlog.append([moves, pos[0], pos[1], mem["H"][pos]])
        if action is None or not env.step(action):
            break
        moves += 1
        path.append(list(env.pos))
    return {"path": path, "ok": env.pos == goal, "H": hlog or None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mssv", action="append")
    ap.add_argument("--mssv-file", default="mssv_list.txt")
    ap.add_argument("--loop-prob", type=float, default=0.08)
    ap.add_argument("--out", default=os.path.join("demo", "demo_thuat_toan.html"))
    args = ap.parse_args()
    mssv_list = args.mssv or read_mssv_file(args.mssv_file)
    if not mssv_list:
        raise SystemExit("Chưa có MSSV. Điền vào mssv_list.txt hoặc dùng --mssv.")

    mazes = []
    for m in mssv_list:
        r, c = maze_size_from_mssv(m)
        maze, start, goal = generate_maze(r, c, seed_from_mssv(m), args.loop_prob)
        mazes.append({"mssv": m, "rows": len(maze), "cols": len(maze[0]), "grid": maze,
                      "start": list(start), "goal": list(goal),
                      "best": shortest_path_length(maze, start, goal),
                      "limit": 10 * len(maze) * len(maze[0])})

    algos = []
    for label, module_name, owner in ALGORITHMS:
        try:
            fn = importlib.import_module(f"algorithms.{module_name}").choose_action
        except ModuleNotFoundError as exc:
            if exc.name == f"algorithms.{module_name}":
                print(f"[THIẾU] {label}: chưa có algorithms/{module_name}.py, bỏ qua")
                continue
            raise
        runs = [run_trace(fn, mz["grid"], tuple(mz["start"]), tuple(mz["goal"]), mz["limit"])
                for mz in mazes]
        algos.append({"label": label, "runs": runs})
        print(f"{label:<14}", [len(r["path"]) - 1 for r in runs], "bước")

    data = {"mazes": mazes, "algos": algos}
    html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    print("Đã ghi", args.out)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Demo thuật toán tìm kiếm trực tuyến trong mê cung</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1d2330;--mute:#5d6678;--line:#dde1e8;--accent:#2457c5;--ok:#1c7c4a;--warn:#b4531b}
*{box-sizing:border-box}
body{margin:0;font-family:"Segoe UI",Roboto,Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.45}
.wrap{max-width:1180px;margin:0 auto;padding:20px 16px 48px}
h1{font-size:1.35rem;margin:0 0 4px}
.sub{color:var(--mute);margin:0 0 16px;font-size:.95rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:14px}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.lbl{font-size:.8rem;color:var(--mute);margin-right:4px}
button{font:inherit;border:1px solid var(--line);background:#fff;border-radius:8px;padding:6px 12px;cursor:pointer;color:var(--ink)}
button:hover{border-color:var(--accent)}
button.on{background:var(--accent);border-color:var(--accent);color:#fff}
button.primary{background:var(--accent);border-color:var(--accent);color:#fff;min-width:96px}
input[type=range]{accent-color:var(--accent)}
#tslider{flex:1;min-width:180px}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(330px,1fr))}
.grid.single{grid-template-columns:minmax(0,760px)}
.panel{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.ph{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin-bottom:6px}
.pn{font-weight:600}
.ps{font-size:.85rem;color:var(--mute);font-variant-numeric:tabular-nums}
.ps.done{color:var(--ok);font-weight:600}
canvas{width:100%;display:block;border-radius:6px;background:#e9ebef}
.legend{display:flex;flex-wrap:wrap;gap:14px;font-size:.85rem;color:var(--mute)}
.sw{display:inline-block;width:14px;height:14px;border-radius:3px;vertical-align:-2px;margin-right:5px;border:1px solid #0002}
table{border-collapse:collapse;width:100%;font-size:.9rem;font-variant-numeric:tabular-nums}
th,td{padding:6px 10px;border-bottom:1px solid var(--line);text-align:right}
th:first-child,td:first-child{text-align:left}
th{color:var(--mute);font-weight:600;font-size:.82rem}
td.best{color:var(--ok);font-weight:700}
.note{font-size:.85rem;color:var(--mute);margin:8px 0 0}
</style>
</head>
<body>
<div class="wrap">
  <h1>Demo thuật toán tìm kiếm trực tuyến trong mê cung</h1>
  <p class="sub">Robot chỉ nhìn thấy 4 ô kề. Vùng xám là chưa biết; ô xanh dương càng đậm thì robot đã ghé càng nhiều lần. Đường đi là kết quả chạy thật của code trong thư mục <code>algorithms/</code>.</p>

  <div class="card">
    <div class="row" style="margin-bottom:10px"><span class="lbl">Mê cung</span><span id="mazeBtns" class="row"></span></div>
    <div class="row" style="margin-bottom:10px"><span class="lbl">Hiển thị</span>
      <button id="modeAll" class="on">Cả 5 thuật toán cùng lúc</button>
      <button id="modeOne">Một thuật toán</button>
      <span id="algoBtns" class="row"></span>
      <label id="hWrap" style="display:none;font-size:.9rem"><input type="checkbox" id="showH"> Hiện giá trị H của LRTA*</label>
    </div>
    <div class="row">
      <button id="play" class="primary">Chạy</button>
      <button id="back">Lùi 1</button>
      <button id="step">Bước tiếp</button>
      <button id="reset">Đặt lại</button>
      <span class="lbl" style="margin-left:8px">Tốc độ</span>
      <input type="range" id="speed" min="1" max="100" value="30" style="width:130px">
      <input type="range" id="tslider" min="0" max="100" value="0">
      <span id="tlabel" class="ps">Bước 0</span>
    </div>
  </div>

  <div id="panels" class="grid"></div>

  <div class="card" style="margin-top:14px">
    <div class="legend">
      <span><i class="sw" style="background:#2c3340"></i>Tường đã thấy</span>
      <span><i class="sw" style="background:#fff"></i>Đường đã thấy</span>
      <span><i class="sw" style="background:#c9ced8"></i>Chưa biết</span>
      <span><i class="sw" style="background:#2457c5"></i>Số lần ghé (đậm dần)</span>
      <span><i class="sw" style="background:#1c9c5b"></i>Đích</span>
      <span><i class="sw" style="background:#e8761a"></i>Robot</span>
    </div>
  </div>

  <div class="card">
    <div class="pn" style="margin-bottom:6px">Kết quả trên mê cung đang chọn</div>
    <table id="tbl"></table>
    <p class="note">Số bước là số lần robot thật sự di chuyển. Tỷ lệ = số bước chia độ dài đường ngắn nhất. Chữ xanh đậm là ít bước nhất.</p>
  </div>

  <div class="card">
    <div class="pn" style="margin-bottom:6px">Tổng hợp trên tất cả mê cung (tỷ lệ số bước / đường ngắn nhất)</div>
    <table id="tblAll"></table>
  </div>
</div>

<script>
const DATA = __DATA__;
const M = DATA.mazes, A = DATA.algos;
const st = {maze:0, t:0, play:false, mode:'all', algo:0, showH:false, acc:0, last:0};

// ---- tiền xử lý: ô nào được nhìn thấy ở bước nào
A.forEach(a => a.runs.forEach((run, mi) => {
  const mz = M[mi], obs = new Int32Array(mz.rows * mz.cols).fill(1e9);
  run.path.forEach((p, k) => {
    [[0,0],[-1,0],[1,0],[0,-1],[0,1]].forEach(d => {
      const r = p[0]+d[0], c = p[1]+d[1];
      if (r>=0 && r<mz.rows && c>=0 && c<mz.cols) { const i = r*mz.cols+c; if (obs[i] > k) obs[i] = k; }
    });
  });
  run.obs = obs;
}));

const $ = id => document.getElementById(id);
const fmt = x => x.toFixed(2).replace('.', ',');

// ---- nút chọn
function buildButtons() {
  $('mazeBtns').innerHTML = '';
  M.forEach((mz, i) => {
    const b = document.createElement('button');
    b.textContent = `${i+1}. MSSV ${mz.mssv} (${mz.rows}×${mz.cols})`;
    b.className = i === st.maze ? 'on' : '';
    b.onclick = () => { st.maze = i; st.t = 0; st.play = false; refresh(true); };
    $('mazeBtns').appendChild(b);
  });
  $('algoBtns').innerHTML = '';
  A.forEach((a, i) => {
    const b = document.createElement('button');
    b.textContent = a.label;
    b.className = (st.mode === 'one' && i === st.algo) ? 'on' : '';
    b.style.display = st.mode === 'one' ? '' : 'none';
    b.onclick = () => { st.algo = i; refresh(true); };
    $('algoBtns').appendChild(b);
  });
  $('modeAll').className = st.mode === 'all' ? 'on' : '';
  $('modeOne').className = st.mode === 'one' ? 'on' : '';
  $('hWrap').style.display = (st.mode === 'one' && A[st.algo].label === 'LRTA*') ? '' : 'none';
}

// ---- bảng
function buildTables() {
  const mz = M[st.maze];
  const rows = A.map(a => { const r = a.runs[st.maze]; const n = r.path.length-1;
    const vis = new Set(r.path.map(p => p.join(','))).size; return {a, r, n, vis}; });
  const minN = Math.min(...rows.filter(x => x.r.ok).map(x => x.n));
  $('tbl').innerHTML = '<tr><th>Thuật toán</th><th>Số bước</th><th>Tỷ lệ</th><th>Ô đã ghé</th><th>Đến đích</th></tr>' +
    rows.map(x => `<tr><td>${x.a.label}</td><td class="${x.r.ok && x.n===minN?'best':''}">${x.n}</td><td>${fmt(x.n/mz.best)}×</td><td>${x.vis}</td><td>${x.r.ok?'Có':'Không'}</td></tr>`).join('') +
    `<tr><td>Đường ngắn nhất</td><td>${mz.best}</td><td>1,00×</td><td></td><td></td></tr>`;
  $('tblAll').innerHTML = '<tr><th>Thuật toán</th>' + M.map((m,i) => `<th>MC${i+1} (${m.rows}×${m.cols})</th>`).join('') + '<th>Trung bình</th></tr>' +
    A.map(a => { const rs = a.runs.map((r,i) => (r.path.length-1)/M[i].best);
      return `<tr><td>${a.label}</td>${rs.map(x => `<td>${fmt(x)}×</td>`).join('')}<td><b>${fmt(rs.reduce((s,x)=>s+x,0)/rs.length)}×</b></td></tr>`; }).join('');
}

// ---- panel
let panels = [];
function buildPanels() {
  const box = $('panels'); box.innerHTML = ''; panels = [];
  box.className = 'grid' + (st.mode === 'one' ? ' single' : '');
  const list = st.mode === 'all' ? A.map((a,i) => i) : [st.algo];
  list.forEach(i => {
    const d = document.createElement('div'); d.className = 'panel';
    d.innerHTML = `<div class="ph"><span class="pn">${A[i].label}</span><span class="ps"></span></div><canvas></canvas>`;
    box.appendChild(d);
    panels.push({i, el:d, cv:d.querySelector('canvas'), ps:d.querySelector('.ps')});
  });
  sizeCanvases();
}
function sizeCanvases() {
  const mz = M[st.maze];
  panels.forEach(p => {
    const w = Math.max(200, p.el.clientWidth - 24);
    const cell = Math.max(4, Math.floor(w / mz.cols));
    const dpr = window.devicePixelRatio || 1;
    p.cell = cell;
    p.cv.width = cell*mz.cols*dpr; p.cv.height = cell*mz.rows*dpr;
    p.cv.style.width = cell*mz.cols+'px'; p.cv.style.height = cell*mz.rows+'px';
    p.dpr = dpr;
  });
}

function maxT() {
  const idx = st.mode === 'all' ? A.map((a,i)=>i) : [st.algo];
  return Math.max(...idx.map(i => A[i].runs[st.maze].path.length-1));
}

function draw(p) {
  const mz = M[st.maze], run = A[p.i].runs[st.maze], n = run.path.length-1;
  const tt = Math.min(st.t, n), c = p.cell, ctx = p.cv.getContext('2d');
  ctx.setTransform(p.dpr,0,0,p.dpr,0,0);
  const cnt = new Uint16Array(mz.rows*mz.cols); let maxc = 1;
  for (let k=0;k<=tt;k++){ const q=run.path[k], i=q[0]*mz.cols+q[1]; cnt[i]++; if(cnt[i]>maxc)maxc=cnt[i]; }
  let Hm = null;
  if (st.showH && st.mode==='one' && run.H) { Hm = new Map(); run.H.forEach(h => { if (h[0] < tt) Hm.set(h[1]*mz.cols+h[2], h[3]); }); }
  for (let r=0;r<mz.rows;r++) for (let col=0;col<mz.cols;col++) {
    const i=r*mz.cols+col, seen = run.obs[i] <= tt;
    let color = '#c9ced8';
    if (seen) color = mz.grid[r][col]===1 ? '#2c3340' : '#ffffff';
    if (seen && mz.grid[r][col]===0 && cnt[i]>0) {
      const a = 0.18 + 0.82*Math.min(1, Math.log(1+cnt[i])/Math.log(1+Math.max(maxc,6)));
      color = `rgba(36,87,197,${a.toFixed(3)})`;
      ctx.fillStyle='#fff'; ctx.fillRect(col*c,r*c,c,c);
    }
    ctx.fillStyle = color; ctx.fillRect(col*c, r*c, c, c);
    if (seen && c >= 9) { ctx.strokeStyle='rgba(0,0,0,.05)'; ctx.strokeRect(col*c+.5, r*c+.5, c-1, c-1); }
    if (Hm && seen && mz.grid[r][col]===0 && c >= 20) {
      const h = Hm.has(i) ? Hm.get(i) : null;
      if (h !== null) { ctx.fillStyle = cnt[i] > 2 ? '#fff' : '#1d2330'; ctx.font = `${Math.floor(c*0.42)}px sans-serif`;
        ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText(String(h), col*c+c/2, r*c+c/2+1); }
    }
  }
  // đích và xuất phát
  ctx.fillStyle = '#1c9c5b'; ctx.fillRect(mz.goal[1]*c, mz.goal[0]*c, c, c);
  ctx.strokeStyle = '#1c7c4a'; ctx.lineWidth = 2; ctx.strokeRect(mz.start[1]*c+1, mz.start[0]*c+1, c-2, c-2); ctx.lineWidth = 1;
  // robot
  const q = run.path[tt]; ctx.fillStyle = '#e8761a'; ctx.beginPath();
  ctx.arc(q[1]*c+c/2, q[0]*c+c/2, Math.max(2.5, c*0.36), 0, Math.PI*2); ctx.fill();
  ctx.strokeStyle='#fff'; ctx.lineWidth=1.5; ctx.stroke(); ctx.lineWidth=1;
  const done = tt >= n;
  p.ps.className = 'ps' + (done && run.ok ? ' done' : '');
  p.ps.textContent = done ? (run.ok ? `Đến đích sau ${n} bước (${fmt(n/mz.best)}×)` : `Dừng sau ${n} bước, chưa tới đích`) : `Bước ${tt}/${n}`;
}

function refresh(rebuild) {
  if (rebuild) { buildButtons(); buildPanels(); buildTables(); const mt = maxT(); $('tslider').max = mt; }
  $('tslider').value = st.t; $('tlabel').textContent = `Bước ${Math.min(st.t, maxT())}/${maxT()}`;
  $('play').textContent = st.play ? 'Tạm dừng' : (st.t >= maxT() ? 'Chạy lại' : 'Chạy');
  panels.forEach(draw);
}

// ---- điều khiển
$('play').onclick = () => { if (st.t >= maxT()) st.t = 0; st.play = !st.play; st.last = 0; refresh(false); if (st.play) requestAnimationFrame(tick); };
$('step').onclick = () => { st.play = false; st.t = Math.min(maxT(), st.t+1); refresh(false); };
$('back').onclick = () => { st.play = false; st.t = Math.max(0, st.t-1); refresh(false); };
$('reset').onclick = () => { st.play = false; st.t = 0; refresh(false); };
$('tslider').oninput = e => { st.play = false; st.t = +e.target.value; refresh(false); };
$('modeAll').onclick = () => { st.mode = 'all'; refresh(true); };
$('modeOne').onclick = () => { st.mode = 'one'; refresh(true); };
$('showH').onchange = e => { st.showH = e.target.checked; refresh(false); };
window.addEventListener('resize', () => { sizeCanvases(); refresh(false); });

function tick(ts) {
  if (!st.play) return;
  if (!st.last) st.last = ts;
  const sps = 1 + Math.pow(+$('speed').value / 100, 2) * 199;   // bước mỗi giây
  st.acc += (ts - st.last) / 1000 * sps; st.last = ts;
  const adv = Math.floor(st.acc); st.acc -= adv;
  if (adv > 0) { st.t = Math.min(maxT(), st.t + adv); }
  if (st.t >= maxT()) st.play = false;
  refresh(false);
  if (st.play) requestAnimationFrame(tick);
}

refresh(true);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
