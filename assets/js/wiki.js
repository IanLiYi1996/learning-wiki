(function () {
  'use strict';
  const core = window.WikiCore;
  const base = document.body.dataset.baseurl || '';
  const currentPath = core.canonicalPath(location.href);
  function icon(name) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'icon');
    svg.setAttribute('width', '20');
    svg.setAttribute('height', '20');
    svg.setAttribute('aria-hidden', 'true');
    const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
    use.setAttribute('href', `${base}/assets/icons.svg#${name}`);
    svg.append(use);
    return svg;
  }
  function clickedBackdrop(event, dialog) {
    if (event.target !== dialog) return false;
    const rect = dialog.getBoundingClientRect();
    return event.clientX < rect.left || event.clientX > rect.right
      || event.clientY < rect.top || event.clientY > rect.bottom;
  }
  document.querySelectorAll('.sidebar-navigation a').forEach(link => {
    if (!link.hash && core.canonicalPath(link.href) === currentPath) {
      link.setAttribute('aria-current', 'page');
      const topic = link.closest('details');
      if (topic) topic.open = true;
    }
  });
  const themeButton = document.querySelector('[data-toggle-theme]');
  function updateThemeButton() {
    const label = document.documentElement.dataset.theme === 'dark' ? '切换浅色模式' : '切换深色模式';
    themeButton.setAttribute('aria-label', label);
    themeButton.title = label;
  }
  updateThemeButton();
  themeButton.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('wiki-theme', next); } catch (_) {}
    updateThemeButton();
  });
  const navigation = document.getElementById('wiki-navigation');
  document.querySelector('[data-open-navigation]').addEventListener('click', () => {
    document.querySelector('[data-navigation-content]')
      .replaceChildren(document.querySelector('.site-sidebar .sidebar-navigation').cloneNode(true));
    navigation.showModal();
  });
  document.querySelector('[data-close-navigation]').addEventListener('click', () => navigation.close());
  navigation.addEventListener('click', event => {
    if (clickedBackdrop(event, navigation) || event.target.closest('a')) navigation.close();
  });
  const article = document.querySelector('.article-content');
  if (article) {
    const toc = document.querySelector('[data-toc]');
    const mobileToc = document.querySelector('[data-mobile-toc]');
    let headingObserver = null;
    function updateOutline() {
      const book = article.querySelector('[data-reading-book]:not([hidden])');
      const scope = book || article;
      document.querySelector('[data-reading-time]').textContent = `约 ${core.readingMinutes(scope.textContent)} 分钟`;
      const headings = Array.from(scope.querySelectorAll('h2[id], h3[id]'));
      toc.replaceChildren();
      mobileToc.querySelector('nav').replaceChildren();
      if (headingObserver) headingObserver.disconnect();
      mobileToc.hidden = !headings.length;
      document.querySelector('[data-toc-panel]').hidden = !headings.length;
      if (!headings.length) return;
      headings.forEach(heading => {
        const a = document.createElement('a');
        a.href = `#${heading.id}`;
        a.textContent = heading.textContent;
        a.dataset.level = heading.tagName.slice(1);
        toc.append(a);
      });
      const mobileNav = mobileToc.querySelector('nav');
      Array.from(toc.children).forEach(link => mobileNav.append(link.cloneNode(true)));
      mobileToc.hidden = false;
      if ('IntersectionObserver' in window) {
        headingObserver = new IntersectionObserver(entries => {
          const visible = entries.filter(entry => entry.isIntersecting)
            .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
          if (!visible.length) return;
          const id = visible[0].target.id;
          Array.from(toc.children).forEach(link => {
            if (decodeURIComponent(link.hash.slice(1)) === id) link.setAttribute('aria-current', 'location');
            else link.removeAttribute('aria-current');
          });
        }, { rootMargin: '-90px 0px -65% 0px' });
        headings.forEach(heading => headingObserver.observe(heading));
      }
    }
    updateOutline();
    mobileToc.querySelector('nav').addEventListener('click', event => {
      if (event.target.closest('a')) mobileToc.open = false;
    });
    document.addEventListener('wiki:reader-change', updateOutline);
    article.querySelectorAll('pre > code').forEach(code => {
      const pre = code.parentElement;
      const outer = pre.closest('[class*="language-"]');
      const match = outer && outer.className.match(/language-([a-z0-9_-]+)/i);
      const wrapper = document.createElement('div');
      wrapper.className = 'code-block';
      pre.parentNode.insertBefore(wrapper, pre);
      const toolbar = document.createElement('div');
      toolbar.className = 'code-toolbar';
      const language = document.createElement('span');
      language.textContent = match ? match[1].toUpperCase() : 'TEXT';
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'icon-button';
      button.setAttribute('aria-label', '复制代码');
      button.title = '复制代码';
      button.append(icon('copy'));
      button.addEventListener('click', async () => {
        let copied = false;
        try {
          await navigator.clipboard.writeText(code.textContent);
          copied = true;
        } catch (_) {
          const range = document.createRange();
          range.selectNodeContents(code);
          const selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
          try { copied = document.execCommand('copy'); } catch (_) {}
          if (copied) selection.removeAllRanges();
        }
        if (copied) {
          button.replaceChildren(icon('check'));
          button.setAttribute('aria-label', '已复制');
          button.title = '已复制';
          setTimeout(() => {
            button.replaceChildren(icon('copy'));
            button.setAttribute('aria-label', '复制代码');
            button.title = '复制代码';
          }, 1600);
        } else {
          button.title = '复制失败，请选择代码复制';
          button.setAttribute('aria-label', button.title);
        }
      });
      toolbar.append(language, button);
      wrapper.append(toolbar, pre);
    });
    let pending = false;
    function updateProgress() {
      const top = article.getBoundingClientRect().top + scrollY;
      const distance = Math.max(1, article.offsetHeight - innerHeight + 92);
      const progress = Math.max(0, Math.min(1, (scrollY - top + 92) / distance));
      document.documentElement.style.setProperty('--reading-progress', progress);
      pending = false;
    }
    function scheduleProgress() { if (!pending) { pending = true; requestAnimationFrame(updateProgress); } }
    addEventListener('scroll', scheduleProgress, { passive: true });
    addEventListener('resize', scheduleProgress);
    document.addEventListener('wiki:reader-change', scheduleProgress);
    updateProgress();
    if (window.MathJax && window.MathJax.startup) window.MathJax.startup.promise.then(scheduleProgress);
    const activeTopic = document.querySelector('.site-sidebar .nav-topic[open]');
    if (activeTopic) {
      const links = Array.from(activeTopic.querySelectorAll('.nav-leaf')).filter(link => !link.hash);
      const index = links.findIndex(link => core.canonicalPath(link.href) === currentPath);
      const pagination = document.querySelector('[data-chapter-pagination]');
      if (index >= 0 && links.length > 1) {
        [-1, 1].forEach(direction => {
          const target = links[index + direction];
          if (!target) { pagination.append(document.createElement('span')); return; }
          const a = document.createElement('a');
          a.href = target.href;
          const text = document.createElement('span');
          const label = document.createElement('small');
          label.textContent = direction < 0 ? '上一篇' : '下一篇';
          text.append(label, document.createTextNode(target.textContent));
          if (direction < 0) a.append(icon('arrow-left'), text);
          else a.append(text, icon('arrow-right'));
          pagination.append(a);
        });
        pagination.hidden = false;
      }
    }
    document.querySelector('[data-back-top]').addEventListener('click', () => {
      scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    });
  }
  const search = document.getElementById('wiki-search');
  const input = document.getElementById('search-input');
  const results = document.querySelector('[data-search-results]');
  const status = document.querySelector('[data-search-status]');
  const retry = document.querySelector('[data-retry-search]');
  let documents = null, loading = null, timer = null;
  function renderResults() {
    if (!documents) return;
    results.replaceChildren();
    const featured = documents.filter(doc => /\/wiki\/topics\/[^/]+\/$/.test(new URL(doc.url).pathname));
    const matches = input.value.trim() ? core.searchDocuments(documents, input.value, 12)
      : (featured.length ? featured : documents.slice(0, 8));
    status.textContent = input.value.trim()
      ? (matches.length ? `${matches.length} 条匹配笔记` : '没有匹配的笔记')
      : `${documents.length} 篇笔记`;
    matches.forEach(doc => {
      const item = document.createElement('li');
      const a = document.createElement('a');
      a.href = doc.url;
      const title = document.createElement('span');
      title.className = 'search-result-title';
      title.textContent = doc.title;
      const text = document.createElement('span');
      text.className = 'search-result-excerpt';
      text.textContent = core.excerpt(doc.text, input.value);
      a.append(title, text);
      item.append(a);
      results.append(item);
    });
  }
  async function loadIndex() {
    if (documents) { renderResults(); return; }
    if (loading) return loading;
    status.textContent = '正在加载笔记…';
    retry.hidden = true;
    loading = (async () => {
      try {
        const version = encodeURIComponent(document.body.dataset.indexVersion || 'local');
        const response = await fetch(`${base}/search.json?v=${version}`);
        if (!response.ok) throw new Error('Index request failed');
        const data = await response.json();
        if (!Array.isArray(data)) throw new Error('Invalid index');
        documents = core.prepareDocuments(data, location.origin, `${base}/`);
        renderResults();
      } catch (_) {
        status.textContent = '笔记索引加载失败';
        retry.hidden = false;
      } finally { loading = null; }
    })();
    return loading;
  }
  function openSearch() { if (!search.open) search.showModal(); input.focus(); loadIndex(); }
  document.querySelector('[data-open-search]').addEventListener('click', openSearch);
  document.querySelector('[data-close-search]').addEventListener('click', () => search.close());
  search.addEventListener('click', event => { if (clickedBackdrop(event, search)) search.close(); });
  retry.addEventListener('click', loadIndex);
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(renderResults, 100); });
  search.addEventListener('keydown', event => {
    const links = Array.from(results.querySelectorAll('a'));
    if (event.key === 'ArrowDown' && links.length) {
      event.preventDefault();
      links[Math.min(links.length - 1, links.indexOf(document.activeElement) + 1)].focus();
    } else if (event.key === 'ArrowUp' && links.length) {
      event.preventDefault();
      const index = links.indexOf(document.activeElement);
      if (index <= 0) input.focus(); else links[index - 1].focus();
    }
  });
  addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); openSearch(); }
  });
})();
