// Read-only checks for fourteen multimodal study pages; no model calls.
(async () => {
  const article = document.querySelector('.article-content');
  if (!article) throw new Error('Missing article');
  const base = document.body.dataset.baseurl;
  const root = `${base}/wiki/topics/deep-learning/vision/`;
  const path = location.pathname.slice(root.length) || 'index.html';
  const counts = {
    'index.html': 1,
    'pixelbench/': 1, 'pixelbench/index.html': 1,
    'pixelbench/representation-and-tasks.html': 2, 'pixelbench/metrics-and-results.html': 1,
    'pixelbench/resolution-and-failure-modes.html': 1, 'pixelbench/prt-training.html': 2,
    'pixelbench/evidence-and-limitations.html': 1, 'pixelbench/lab.html': 1,
    'pixelbench/sources.html': 0,
    'embeddinggemma-2/': 1, 'embeddinggemma-2/index.html': 1,
    'embeddinggemma-2/architecture.html': 1, 'embeddinggemma-2/training-recipe.html': 1,
    'embeddinggemma-2/evaluation-and-deployment.html': 1, 'embeddinggemma-2/sources.html': 0
  };
  if (!location.pathname.startsWith(root) || counts[path] === undefined) {
    throw new Error('Unknown study route');
  }
  const images = [...article.querySelectorAll('.wiki-figure img')];
  if (images.length !== counts[path]) throw new Error('Figure count');
  for (const image of images) {
    image.loading = 'eager';
    await image.decode();
    const url = new URL(image.currentSrc);
    if (url.origin !== location.origin || !/\/(?:rep|pxb|eg2)-[a-z0-9-]+\.svg$/.test(url.pathname) ||
        !image.alt || !image.naturalWidth ||
        !image.closest('figure')?.querySelector('figcaption')) throw new Error('Figure contract');
  }
  await window.MathJax.startup.promise;
  if (article.querySelector('mjx-merror, [data-mjx-error]')) throw new Error('Invalid math');
  const equations = article.querySelectorAll('mjx-container').length;
  if (['pixelbench/representation-and-tasks.html', 'pixelbench/metrics-and-results.html',
       'pixelbench/prt-training.html'].includes(path) && equations < 1) throw new Error('Missing math');
  const title = article.querySelector('h1')?.textContent.trim();
  if (!title || !document.title.startsWith(`${title} |`)) throw new Error('Title');
  const ids = [...document.querySelectorAll('[id]')].map(node => node.id);
  if (new Set(ids).size !== ids.length) throw new Error('Duplicate IDs');
  const topic = document.querySelector(`.nav-topic[data-topic="${base}/wiki/topics/deep-learning/"]`);
  const groups = [...topic.querySelectorAll('.nav-subtopic')];
  const opened = groups.filter(group => group.open);
  if (!topic.open || groups.length !== 7 || opened.length !== 1 ||
      opened[0].dataset.subtopic !== '视觉表征与多模态') throw new Error('Subgroup navigation');
  const records = await fetch(`${base}/search.json`).then(response => {
    if (!response.ok) throw new Error('Search response');
    return response.json();
  });
  const book = records.filter(row => new URL(row.url, location.origin).pathname.startsWith(root));
  if (book.length !== 14 || new Set(book.map(row => row.url)).size !== 14) throw new Error('Search scope');
  if (book.find(row => new URL(row.url, location.origin).pathname === location.pathname)?.title !== title) {
    throw new Error('Search title');
  }
  const toc = [...document.querySelectorAll('[data-toc] a')];
  if (!toc.length) throw new Error('Missing TOC');
  for (const link of toc) {
    if (!document.getElementById(decodeURIComponent(link.hash.slice(1)))) throw new Error('TOC target');
  }
  const pager = document.querySelector('[data-chapter-pagination]');
  if (!pager || pager.hidden) throw new Error('Missing pagination');
  const neighbors = [...pager.querySelectorAll('a')].map(link => new URL(link.href).pathname);
  if (neighbors.some(path => !path.startsWith(root) &&
      path !== `${base}/wiki/topics/deep-learning/`)) {
    throw new Error('Group-scoped pagination');
  }
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth) {
    throw new Error('Horizontal overflow');
  }
  return {page: location.pathname, viewport: innerWidth, figures: images.length, equations,
    searchPages: book.length, toc: toc.length, pagination: neighbors,
    version: document.body.dataset.indexVersion};
})();
