// Open /wiki/topics/physical-ai/ first; execute with agent-browser eval --stdin.
(async () => {
  const reader = document.querySelector('[data-physical-reader]');
  if (!reader) throw new Error('No complete in-page reader');
  const path = location.pathname, origin = performance.timeOrigin;
  const lastChapters = {
    knowledge: '十五、练习与掌握程度检查',
    industry: '12 把产品接起来：交付接口与原理对照',
    advanced: '14 数值练习与系统贯通：把公式变成可检查的计算',
    gtc: '八、相关会议场次',
  };
  const report = { books: [], samePage: true, mathErrors: 0 };
  async function waitFor(predicate) {
    for (let attempt = 0; attempt < 150; attempt++) {
      if (predicate()) return;
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error('Reader did not reach the expected state');
  }
  for (const [key, lastChapter] of Object.entries(lastChapters)) {
    reader.querySelector('[data-reader-link="' + key + '"]').click();
    await waitFor(() => !document.getElementById('reader-' + key).hidden);
    const panel = document.getElementById('reader-' + key);
    if (!panel.textContent.includes(lastChapter)) throw new Error('Truncated book: ' + key);
    if (document.querySelectorAll('[data-reading-book]:not([hidden])').length !== 1) {
      throw new Error('More than one visible book');
    }
    const toc = [...document.querySelectorAll('[data-toc] a')];
    if (!toc.length || toc.some(link => !decodeURIComponent(link.hash).startsWith('#reader-' + key + '--'))) {
      throw new Error('Outline points to another book: ' + key);
    }
    const selected = reader.querySelector('[data-reader-link="' + key + '"]');
    if (selected.getAttribute('aria-current') !== 'location') throw new Error('Selected link not announced');
    if (key === 'advanced') {
      await waitFor(() => panel.querySelectorAll('mjx-container[display="true"]').length === 109);
      const errors = panel.querySelectorAll('mjx-merror').length;
      if (errors) throw new Error('Math errors in the principles book');
      report.mathErrors += errors;
      report.displayFormulas = 109;
    }
    report.books.push({ key, headings: toc.length, figures: panel.querySelectorAll('.wiki-figure').length });
    if (location.pathname !== path || performance.timeOrigin !== origin) {
      throw new Error('A book selection navigated away instead of switching in-page');
    }
  }
  const endAnchor = document.querySelector('#reader-gtc .reader-chapter-directory a:last-child');
  endAnchor.click();
  const target = document.getElementById(decodeURIComponent(endAnchor.hash.slice(1)));
  if (!target || target.closest('[hidden]')) throw new Error('Final appendix anchor cannot be read');
  if (document.documentElement.scrollWidth > innerWidth) throw new Error('Reader overflows viewport');
  report.finalAppendix = target.textContent;
  history.replaceState(null, '', location.pathname);
  dispatchEvent(new PopStateEvent('popstate'));
  await waitFor(() => !document.getElementById('reader-knowledge').hidden);
  reader.querySelector('[data-reader-link="industry"]').click();
  reader.querySelector('[data-reader-link="advanced"]').click();
  history.back();
  await waitFor(() => location.hash === '#reader-industry'
    && !document.getElementById('reader-industry').hidden);
  history.back();
  await waitFor(() => !location.hash && !document.getElementById('reader-knowledge').hidden);
  history.forward();
  await waitFor(() => location.hash === '#reader-industry'
    && !document.getElementById('reader-industry').hidden);
  if (location.pathname !== path || performance.timeOrigin !== origin) throw new Error('History caused a reload');
  report.historyBackForward = true;
  return report;
})();
