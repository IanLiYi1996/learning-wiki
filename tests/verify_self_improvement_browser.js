// Read-only browser contract for the twelve RSI study pages, no model calls.
(async () => {
  if (document.readyState === 'loading') {
    await new Promise(resolve => document.addEventListener('DOMContentLoaded', resolve, { once: true }));
  }
  const base = document.body.dataset.baseurl;
  const root = `${base}/wiki/topics/deep-learning/self-improvement/`;
  const path = location.pathname.slice(root.length) || 'index.html';
  const counts = {
    'index.html': 1,
    'concepts-and-foundations.html': 1,
    'agent-evolution.html': 1,
    'learning-and-weights.html': 1,
    'algorithms-and-infrastructure.html': 1,
    'ai-scientists.html': 1,
    'industry-and-autoresearch.html': 1,
    'evaluation-and-safety.html': 1,
    'research-roadmap.html': 2,
    'glossary.html': 0,
    'lab.html': 2,
    'sources.html': 0,
  };
  if (!location.pathname.startsWith(root) || counts[path] === undefined) {
    throw new Error('Unknown RSI page');
  }
  const article = document.querySelector('.article-content');
  if (!article) throw new Error('Missing article');
  const title = article.querySelector('h1')?.textContent.trim();
  if (!title || !document.title.startsWith(`${title} |`)) throw new Error('Title mismatch');
  const images = [...article.querySelectorAll('.wiki-figure img')];
  if (images.length !== counts[path]) throw new Error(`Figure count: ${images.length}`);
  for (const image of images) {
    image.loading = 'eager';
    await image.decode();
    const asset = new URL(image.currentSrc);
    if (!image.naturalWidth || !image.alt || asset.origin !== location.origin ||
        !/\/images\/rsi-[a-z0-9-]+\.svg$/.test(asset.pathname) ||
        !image.closest('figure')?.querySelector('figcaption')) {
      throw new Error('Local SVG/caption contract');
    }
  }
  const ids = [...document.querySelectorAll('[id]')].map(node => node.id);
  if (new Set(ids).size !== ids.length) throw new Error('Duplicate IDs');
  const topic = document.querySelector(`.nav-topic[data-topic="${base}/wiki/topics/deep-learning/"]`);
  const groups = [...topic.querySelectorAll('.nav-subtopic')];
  const opened = groups.filter(group => group.open);
  if (!topic.open || groups.length !== 6 || opened.length !== 1 ||
      opened[0].dataset.subtopic !== '自动研究与评测') {
    throw new Error('Current subgroup navigation');
  }
  const records = await fetch(`${base}/search.json`).then(response => {
    if (!response.ok) throw new Error('Search response');
    return response.json();
  });
  const book = records.filter(row => new URL(row.url, location.origin).pathname.startsWith(root));
  if (book.length !== 12 || new Set(book.map(row => row.url)).size !== 12) {
    throw new Error('Search scope');
  }
  const canonical = value => new URL(value, location.origin).pathname.replace(/\/index\.html$/, '/');
  if (book.find(row => canonical(row.url) === canonical(location.href))?.title !== title) {
    throw new Error('Search title');
  }
  const toc = [...document.querySelectorAll('[data-toc] a')];
  if (!toc.length || toc.some(link => !document.getElementById(decodeURIComponent(link.hash.slice(1))))) {
    throw new Error('TOC contract');
  }
  const pager = document.querySelector('[data-chapter-pagination]');
  if (!pager || pager.hidden) throw new Error('Missing chapter pagination');
  const neighbors = [...pager.querySelectorAll('a')].map(link => new URL(link.href).pathname);
  const allowed = new Set([
    `${base}/wiki/topics/deep-learning/`,
    `${base}/wiki/topics/deep-learning/diffusion/04-autoresearch-and-oracles.html`,
  ]);
  if (neighbors.some(path => !path.startsWith(root) && !allowed.has(path))) {
    throw new Error('Pagination left the research subgroup');
  }
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth) {
    throw new Error('Horizontal page overflow');
  }
  if (/\[\^\d+\]|\]\([^)]*\.md/.test(article.innerText)) throw new Error('Unrendered Markdown');
  return { page: location.pathname, viewport: innerWidth, figures: images.length,
    searchPages: book.length, toc: toc.length, pagination: neighbors };
})();
