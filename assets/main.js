(() => {
  'use strict';
  const root = document.documentElement;
  const dialog = document.getElementById('bibtex-dialog');
  const code = document.getElementById('bibtex-code');
  const status = document.getElementById('copy-status');
  let currentPaper;
  let opener;
  const language = () => root.lang === 'zh' ? 'zh' : 'en';
  const text = (en, zh) => language() === 'zh' ? zh : en;
  function updateLanguage(lang) {
    root.lang = lang;
    try { localStorage.setItem('feng-li-language', lang); } catch {}
    document.querySelectorAll('[data-set-language]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.setLanguage === lang)));
    const search = document.getElementById('publication-search');
    if (search) search.placeholder = text('Search papers, journals, or topics…', '检索论文标题、期刊或英文关键词…');
    const allYears = document.querySelector('#publication-year option[value="all"]');
    if (allYears) allYears.textContent = text('All years', '全部年份');
    filterPapers();
    document.title = ({home: text('Feng Li | Beihang University', '李峰 | 北京航空航天大学'), research: text('Research | Feng Li', '科研工作 | 李峰'), publications: text('Publications | Feng Li', '主要论著 | 李峰')})[document.body.dataset.page];
  }
  document.querySelectorAll('[data-set-language]').forEach(button => button.addEventListener('click', () => updateLanguage(button.dataset.setLanguage)));
  function filterPapers() {
    const input = document.getElementById('publication-search');
    if (!input) return;
    const query = input.value.toLocaleLowerCase().trim();
    const year = document.getElementById('publication-year').value;
    let count = 0;
    document.querySelectorAll('#publication-list .publication').forEach(article => {
      const matches = (!query || article.dataset.search.toLocaleLowerCase().includes(query)) && (year === 'all' || article.dataset.year === year);
      article.hidden = !matches;
      if (matches) count++;
    });
    document.getElementById('publication-count').textContent = text(`${count} ${count === 1 ? 'paper' : 'papers'}`, `共 ${count} 篇`);
    document.getElementById('no-results').hidden = count !== 0;
  }
  document.getElementById('publication-search')?.addEventListener('input', filterPapers);
  document.getElementById('publication-year')?.addEventListener('change', filterPapers);
  document.querySelectorAll('[data-bibtex]').forEach(button => button.addEventListener('click', () => {
    currentPaper = window.PUBLICATIONS.find(paper => paper.id === button.dataset.bibtex);
    if (!currentPaper) return;
    opener = button;
    code.textContent = currentPaper.bibtex;
    document.getElementById('bibtex-paper-title').textContent = currentPaper.title;
    document.getElementById('download-bibtex').href = `assets/bibtex/${currentPaper.id}.bib`;
    document.getElementById('download-bibtex').textContent = text('Download .bib', '下载 .bib');
    status.textContent = '';
    dialog.showModal();
  }));
  document.getElementById('close-bibtex').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) {
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  }});
  dialog.addEventListener('close', () => opener?.focus());
  document.getElementById('copy-bibtex').addEventListener('click', async () => {
    if (!currentPaper) return;
    let copied = false;
    try {
      await navigator.clipboard.writeText(currentPaper.bibtex);
      copied = true;
    } catch {
      const area = document.createElement('textarea');
      area.value = currentPaper.bibtex;
      area.style.position = 'fixed';
      area.style.opacity = '0';
      dialog.append(area);
      area.focus(); area.select();
      try { copied = document.execCommand('copy'); } catch {}
      area.remove();
      document.getElementById('copy-bibtex').focus();
    }
    status.textContent = copied ? text('BibTeX copied to clipboard.', 'BibTeX 已复制。') : text('Select and copy the text above, or download the .bib file.', '请选择上方文本复制，或下载 .bib 文件。');
  });
  updateLanguage(language());
})();
