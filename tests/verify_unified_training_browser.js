// Read-only study QA: no training, model calls, or execution of paper examples.
(async () => {
  const article = document.querySelector('.article-content');
  if (!article) throw new Error('Missing article');
  const base = document.body.dataset.baseurl;
  const root = `${base}/wiki/topics/deep-learning/training/unified-training/`;
  const name = location.pathname.slice(root.length) || 'index.html';
  const counts = {'index.html': 1, 'likelihood-and-targets.html': 1,
    'maxrl-and-finite-sampling.html': 2, 'weighted-loss-and-masks.html': 1,
    'asynchronous-system.html': 2, 'mixing-and-schedules.html': 1,
    'evidence-and-limits.html': 1, 'lab.html': 1, 'sources.html': 0};
  if (!location.pathname.startsWith(root) || counts[name] === undefined) throw new Error('Unknown route');
  const title = article.querySelector('h1')?.textContent.trim();
  if (!title || !document.title.startsWith(`${title} |`)) throw new Error('Title');
  const figures = [...article.querySelectorAll('.wiki-figure img')];
  if (figures.length !== counts[name]) throw new Error('Figure count');
  for (const image of figures) {
    image.loading = 'eager';
    await image.decode();
    const url = new URL(image.currentSrc);
    if (url.origin !== location.origin || !/\/uni-[a-z0-9-]+\.svg$/.test(url.pathname) ||
        !image.alt || !image.naturalWidth ||
        !image.closest('figure')?.querySelector('figcaption')) throw new Error('Figure contract');
  }
  await window.MathJax.startup.promise;
  if (article.querySelector('mjx-merror, [data-mjx-error]')) throw new Error('Invalid math');
  const equations = article.querySelectorAll('mjx-container').length;
  if (['likelihood-and-targets.html', 'maxrl-and-finite-sampling.html',
       'weighted-loss-and-masks.html', 'mixing-and-schedules.html'].includes(name) &&
      equations < 1) throw new Error('Missing math');
  const ids = [...document.querySelectorAll('[id]')].map(node => node.id);
  if (new Set(ids).size !== ids.length) throw new Error('Duplicate IDs');
  const topic = document.querySelector(`.nav-topic[data-topic="${base}/wiki/topics/deep-learning/"]`);
  const groups = [...topic.querySelectorAll('.nav-subtopic')];
  const opened = groups.filter(group => group.open);
  if (!topic.open || opened.length !== 1 || opened[0].dataset.subtopic !== 'LLM 训练与后训练') {
    throw new Error('Wrong training group');
  }
  const records = await fetch(`${base}/search.json`).then(response => {
    if (!response.ok) throw new Error('Search response');
    return response.json();
  });
  const selected = records.filter(row => new URL(row.url, location.origin).pathname.startsWith(root));
  if (selected.length !== 9 || new Set(selected.map(row => row.url)).size !== 9) throw new Error('Search scope');
  if (selected.find(row => new URL(row.url, location.origin).pathname === location.pathname)?.title !== title) {
    throw new Error('Search title');
  }
  const toc = [...document.querySelectorAll('[data-toc] a')];
  if (!toc.length || toc.some(link => !document.getElementById(decodeURIComponent(link.hash.slice(1))))) {
    throw new Error('TOC targets');
  }
  const pager = document.querySelector('[data-chapter-pagination]');
  if (!pager || pager.hidden) throw new Error('Missing pagination');
  const neighbors = [...pager.querySelectorAll('a')].map(link => new URL(link.href).pathname);
  if (neighbors.some(path => !path.startsWith(`${base}/wiki/topics/deep-learning/training/`) &&
      path !== `${base}/wiki/topics/deep-learning/`)) throw new Error('Cross-group pagination');
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth) {
    throw new Error('Page overflow');
  }
  return {page: location.pathname, viewport: innerWidth, figures: figures.length, equations,
    searchPages: selected.length, toc: toc.length, pagination: neighbors,
    version: document.body.dataset.indexVersion};
})();
