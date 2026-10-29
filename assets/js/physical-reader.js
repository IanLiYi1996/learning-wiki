(function () {
  'use strict';
  const reader = document.querySelector('[data-physical-reader]');
  if (!reader) return;
  const books = Array.from(reader.querySelectorAll('[data-reading-book]'));
  let active = null;
  let mathQueue = Promise.resolve();
  const switcher = reader.querySelector('.reader-switcher');
  function measureSwitcher() {
    reader.style.setProperty('--reader-switcher-height', switcher.offsetHeight + 'px');
  }

  function decodedHash() {
    try { return decodeURIComponent(location.hash.slice(1)); } catch (_) { return ''; }
  }
  function bookForHash(hash) {
    return books.find(book => hash === book.id || hash.startsWith(book.id + '--'));
  }
  function announce() {
    document.dispatchEvent(new CustomEvent('wiki:reader-change', { detail: { book: active } }));
  }
  function updateLinks() {
    reader.querySelectorAll('[data-reader-link]').forEach(link => {
      if (link.dataset.readerLink === active.dataset.readingBook) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    document.querySelectorAll('.sidebar-navigation a').forEach(link => {
      const url = new URL(link.href);
      if (!url.hash.startsWith('#reader-')) return;
      const selected = url.hash === '#' + active.id;
      if (selected) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }
  function activate(book) {
    if (!book) return;
    const changed = active !== book;
    active = book;
    books.forEach(candidate => {
      candidate.hidden = candidate !== active;
      candidate.classList.toggle('reader-inactive', candidate !== active);
    });
    updateLinks();
    announce();
    if (changed && window.MathJax && window.MathJax.startup) {
      const selected = book;
      // Render only the newly selected book, without re-typesetting hidden books.
      mathQueue = mathQueue.catch(() => {}).then(() => window.MathJax.startup.promise)
        .then(() => selected === active ? window.MathJax.typesetPromise([selected]) : undefined)
        .then(announce)
        .catch(() => {}); // Source TeX stays readable if the optional CDN fails.
    }
  }
  function followHash(scroll) {
    const hash = decodedHash();
    const targetBook = bookForHash(hash);
    if (targetBook) activate(targetBook);
    if (!scroll || !hash) return;
    const target = document.getElementById(hash);
    if (!target) return;
    let ancestor = target.parentElement;
    while (ancestor) {
      if (ancestor.tagName === 'DETAILS') ancestor.open = true;
      ancestor = ancestor.parentElement;
    }
    target.scrollIntoView({ block: 'start' });
  }
  reader.classList.add('reader-enhanced');
  measureSwitcher();
  addEventListener('resize', measureSwitcher);
  if ('ResizeObserver' in window) new ResizeObserver(measureSwitcher).observe(switcher);
  activate(bookForHash(decodedHash()) || books[0]);
  if (location.hash) requestAnimationFrame(() => followHash(true));

  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const url = new URL(link.href);
    if (url.origin !== location.origin
      || window.WikiCore.canonicalPath(url.href) !== window.WikiCore.canonicalPath(location.href)) return;
    let hash;
    try { hash = decodeURIComponent(url.hash.slice(1)); } catch (_) { return; }
    if (!bookForHash(hash)) return;
    event.preventDefault();
    history.pushState(null, '', url.hash);
    followHash(true);
  });
  addEventListener('hashchange', () => followHash(true));
  addEventListener('popstate', () => {
    if (!location.hash) activate(books[0]);
    else followHash(true);
  });
})();
