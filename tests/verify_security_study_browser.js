// Read-only layout, images, math, search and chapter navigation checks.
(async () => {
  const article = document.querySelector('.article-content');
  if (!article) throw new Error('Missing article');
  const name = location.pathname.split('/').pop() || 'index.html';
  const hub = !location.pathname.includes('/aws-continuum/');
  const counts = { 'index.html': 1, 'security-foundations.html': 1,
    'continuum-l200.html': 2, 'permissions-and-data.html': 1,
    'validation-and-remediation.html': 1, 'customer-solutions.html': 2,
    'learning-roadmap.html': 1, 'lab.html': 1, 'sources.html': 0 };
  const expected = hub ? 0 : counts[name];
  if (expected === undefined) throw new Error('Unknown page');
  const images = Array.from(article.querySelectorAll('img'));
  if (images.length !== expected) throw new Error('Image count');
  for (const image of images) {
    image.loading = 'eager';
    await image.decode();
    if (!image.naturalWidth || !image.alt) throw new Error('Image decode/alt');
    const url = new URL(image.currentSrc);
    if (url.origin !== location.origin || !url.pathname.endsWith('.svg')) {
      throw new Error('Missing local SVG or enhancement');
    }
    if (!url.pathname.endsWith('/sec-aws-governance.svg') &&
        !image.closest('figure')?.querySelector('figcaption')) throw new Error('Caption');
  }
  await window.MathJax.startup.promise;
  if (article.querySelector('mjx-merror, [data-mjx-error]')) throw new Error('Equation error');
  if (article.querySelectorAll('mjx-container').length !== (!hub && name === 'lab.html' ? 2 : 0)) {
    throw new Error('Unexpected math: currency must not become an equation');
  }
  const title = article.querySelector('h1')?.textContent.trim();
  if (!title || !document.title.startsWith(`${title} |`)) throw new Error('Title');
  const ids = Array.from(document.querySelectorAll('[id]'), node => node.id);
  if (new Set(ids).size !== ids.length) throw new Error('Duplicate IDs');
  const base = document.body.dataset.baseurl;
  const topic = document.querySelector(`.nav-topic[data-topic="${base}/wiki/topics/security/"]`);
  if (!topic?.open || topic.querySelector('.nav-subtopic')) throw new Error('Topic navigation');
  const records = await fetch(`${base}/search.json`).then(response => response.json());
  const selected = records.filter(row => new URL(row.url, location.origin).pathname.startsWith(
    `${base}/wiki/topics/security/`));
  if (selected.length !== 10 || new Set(selected.map(row => row.url)).size !== 10) {
    throw new Error('Search routes');
  }
  if (selected.find(row => new URL(row.url, location.origin).pathname === location.pathname)?.title !== title) {
    throw new Error('Search title');
  }
  const pagination = document.querySelector('[data-chapter-pagination]');
  if (!pagination || pagination.hidden) throw new Error('Missing pagination');
  const neighbors = Array.from(pagination.querySelectorAll('a'), link => new URL(link.href).pathname);
  if (neighbors.some(path => !path.startsWith(`${base}/wiki/topics/security/`))) {
    throw new Error('Cross-topic pagination');
  }
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth) {
    throw new Error('Horizontal page overflow');
  }
  return {page: location.pathname, viewport: innerWidth, images: images.length,
    equations: article.querySelectorAll('mjx-container').length, searchPages: selected.length,
    version: document.body.dataset.indexVersion};
})();
