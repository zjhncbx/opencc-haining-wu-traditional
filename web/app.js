/* 在线转换页面的交互层。依赖 dicts.js（数据）与 engine.js（转换引擎）。 */
;(function () {
  'use strict';

  const DATA = window.HN_DATA;
  const ENGINE = window.HN_ENGINE.createEngine(DATA);
  const $ = function (id) { return document.getElementById(id); };

  const state = {
    scheme: DATA.schemes[0].id,
    result: null,
    highlight: true,
    onlyChanged: true
  };

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  let toastTimer = null;
  function toast(msg) {
    const el = $('toast');
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove('show'); }, 1800);
  }

  function currentScheme() {
    return ENGINE.schemes.filter(function (s) { return s.id === state.scheme; })[0];
  }

  // ---------- 转换方向 ----------
  function buildModes() {
    const box = $('mode-list');
    box.innerHTML = '';
    ENGINE.schemes.forEach(function (s) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'mode-btn' + (s.id === state.scheme ? ' active' : '');
      btn.textContent = s.label;
      btn.title = s.desc;
      btn.dataset.scheme = s.id;
      btn.addEventListener('click', function () {
        const prev = currentScheme();
        const input = $('input');
        // 若输入框里还是上一个方向的示例（或干脆是空的），换成新方向的示例，
        // 避免切换方向后拿一段简体文本去试「任意繁 → 修订繁」这类方向。
        if (!input.value.trim() || input.value === prev.sample) input.value = s.sample;
        state.scheme = s.id;
        Array.prototype.forEach.call(box.children, function (b) {
          b.classList.toggle('active', b.dataset.scheme === s.id);
        });
        $('mode-desc').textContent = s.desc;
        render();
      });
      box.appendChild(btn);
    });
    $('mode-desc').textContent = currentScheme().desc;
  }

  // ---------- 结果 / 高亮 ----------
  function renderOutput() {
    const r = state.result;
    const out = $('output');
    if (!r || !r.text) { out.innerHTML = ''; return; }
    let html = '';
    r.segments.forEach(function (seg) {
      const text = esc(seg.text);
      if (state.highlight && seg.changed && seg.text) {
        const tip = esc('规则：' + seg.dict + ' ｜ 原：' + seg.src);
        html += '<mark title="' + tip + '">' + text + '</mark>';
      } else {
        html += text;
      }
    });
    out.innerHTML = html;
  }

  function renderHits() {
    const r = state.result;
    const tbody = $('hit-table').querySelector('tbody');
    if (!r) { tbody.innerHTML = ''; return; }
    const all = r.hits;
    const changed = all.filter(function (h) { return h.changed; });
    const list = state.onlyChanged ? changed : all;
    const shown = list.slice(0, 300);
    $('hit-summary').textContent = '共 ' + all.length + ' 条命中，其中 ' + changed.length + ' 条有改动' +
      (list.length > shown.length ? '（下表只列前 300 条）' : '');
    tbody.innerHTML = shown.map(function (h) {
      return '<tr' + (h.changed ? '' : ' class="identity"') + '>' +
        '<td>' + h.pos + '</td>' +
        '<td><code>' + esc(h.src) + '</code></td>' +
        '<td><code>' + esc(h.text) + '</code></td>' +
        '<td class="dict"><code>' + esc(h.dict || '—') + '</code></td>' +
        '</tr>';
    }).join('');
    if (!shown.length) {
      tbody.innerHTML = '<tr><td colspan="4" class="muted">没有命中的规则（本方案对这段文本不做改动）。</td></tr>';
    }
  }

  function render() {
    const text = $('input').value;
    state.result = ENGINE.convert(text, state.scheme);
    $('in-count').textContent = Array.from(text).length + ' 字';
    $('out-count').textContent = Array.from(state.result.text).length + ' 字';
    renderOutput();
    renderHits();
  }

  // ---------- 自检 ----------
  function runSelfTest() {
    const results = ENGINE.runCases();
    const passed = results.filter(function (r) { return r.pass; }).length;
    const failed = results.length - passed;
    const byScheme = {};
    results.forEach(function (r) {
      if (!byScheme[r.scheme]) byScheme[r.scheme] = { ok: 0, total: 0 };
      byScheme[r.scheme].total++;
      if (r.pass) byScheme[r.scheme].ok++;
    });
    let html = '<div class="test-summary">' +
      '<span class="pill ' + (failed ? 'bad' : 'ok') + '">' +
      passed + '/' + results.length + ' 通过</span>' +
      '<span class="muted">覆盖 ' + Object.keys(byScheme).length + ' 个转换方向，' +
      '用的是本页同一套引擎与字典</span></div>';
    html += '<ul class="test-list">' + Object.keys(byScheme).map(function (s) {
      const v = byScheme[s];
      return '<li><code>' + esc(s) + '</code>：' + v.ok + '/' + v.total +
        (v.ok === v.total ? ' ✓' : ' ✗') + '</li>';
    }).join('') + '</ul>';
    if (failed) {
      html += '<table class="fail-table"><thead><tr><th>方案</th><th>输入</th><th>预期</th><th>实际</th></tr></thead><tbody>' +
        results.filter(function (r) { return !r.pass; }).map(function (r) {
          return '<tr><td>' + esc(r.scheme) + '</td><td>' + esc(r.input) +
            '</td><td>' + esc(r.expected) + '</td><td>' + esc(r.actual) + '</td></tr>';
        }).join('') + '</tbody></table>';
    }
    $('test-result').innerHTML = html;
    toast(failed ? '有 ' + failed + ' 条用例未通过' : '全部用例通过');
  }

  // ---------- 剪贴板 / 下载 ----------
  async function copyText(text) {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch (e) { /* file:// 下常被拒绝，走兜底 */ }
    try {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand('copy');
      document.body.removeChild(ta);
      return ok;
    } catch (e2) { return false; }
  }

  function download(text) {
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'converted-' + state.scheme + '.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  const ACTIONS = {
    sample: function () {
      $('input').value = currentScheme().sample;
      render();
      toast('已填入当前方向的示例文本');
    },
    clear: function () { $('input').value = ''; render(); $('input').focus(); },
    paste: async function () {
      try {
        const t = await navigator.clipboard.readText();
        $('input').value = t;
        render();
        toast('已粘贴');
      } catch (e) {
        $('input').focus();
        toast('浏览器未允许读取剪贴板，请按 Ctrl+V');
      }
    },
    copy: async function () {
      const ok = await copyText(state.result ? state.result.text : '');
      toast(ok ? '已复制转换结果' : '复制失败，请手动选中结果');
    },
    swap: function () {
      $('input').value = state.result ? state.result.text : '';
      render();
      toast('结果已送回输入框');
    },
    download: function () {
      download(state.result ? state.result.text : '');
      toast('已下载');
    },
    selftest: runSelfTest
  };

  document.addEventListener('click', function (e) {
    const btn = e.target.closest ? e.target.closest('button[data-act]') : null;
    if (btn && ACTIONS[btn.dataset.act]) ACTIONS[btn.dataset.act]();
  });

  let inputTimer = null;
  $('input').addEventListener('input', function () {
    clearTimeout(inputTimer);
    inputTimer = setTimeout(render, 50);
  });
  $('highlight').addEventListener('change', function (e) {
    state.highlight = e.target.checked;
    renderOutput();
  });
  $('only-changed').addEventListener('change', function (e) {
    state.onlyChanged = e.target.checked;
    renderHits();
  });
  $('font-size').addEventListener('change', function (e) {
    $('workspace').style.setProperty('--pane-size', e.target.value + 'px');
  });
  $('font-family').addEventListener('change', function (e) {
    const v = { sans: 'var(--sans)', serif: 'var(--serif)', mono: 'var(--mono)' }[e.target.value];
    $('workspace').style.setProperty('--pane-font', v);
  });

  // ---------- 初始化 ----------
  const meta = ENGINE.meta;
  $('meta-line').textContent = '字典 ' + Object.keys(meta.dicts).length + ' 个 · ' +
    (meta.total_bytes / 1048576).toFixed(2) + ' MB · 生成 ' + meta.generated;
  $('test-meta').textContent = meta.case_count + ' 条用例';
  $('footer-meta').textContent = meta.project + ' ｜ ' + meta.matching + ' ｜ ' + meta.note;
  buildModes();
  $('input').value = currentScheme().sample;
  render();
  runSelfTest();
})();
