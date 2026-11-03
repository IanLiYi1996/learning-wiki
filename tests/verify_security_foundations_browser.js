// Read-only checks for the fourteen new study pages, never test real targets.
(async () => {
  const article = document.querySelector('.article-content');
  if (!article) throw new Error('Missing article');
  const counts = {
    'index.html': 1, '01-risk-and-governance.html': 1, '02-identity-and-organization.html': 1,
    '03-network-and-zero-trust.html': 1, '04-data-keys-and-privacy.html': 1,
    '05-app-and-api-security.html': 1, '06-devsecops-and-supply-chain.html': 2,
    '07-workload-and-container-security.html': 1, '08-detection-and-incident-response.html': 2,
    '09-ai-and-agent-security.html': 2, '10-resilience-and-recovery.html': 1,
    'learning-roadmap.html': 1, 'lab.html': 1, 'sources.html': 0
  };
  const name = location.pathname.split('/').pop() || 'index.html';
  if (counts[name] === undefined || !location.pathname.includes('/security-101/')) {
    throw new Error('Unknown foundations route');
  }
  const images = [...article.querySelectorAll('img')];
  if (images.length !== counts[name]) throw new Error('Figure count');
  for (const image of images) {
    image.loading = 'eager';
    await image.decode();
    const url = new URL(image.currentSrc);
    if (!image.alt || !image.naturalWidth || url.origin !== location.origin ||
        !/\/safe-[a-z0-9-]+\.svg$/.test(url.pathname) ||
        !image.closest('figure')?.querySelector('figcaption')) throw new Error('Figure contract');
  }
  await window.MathJax.startup.promise;
  if (article.querySelector('mjx-container, mjx-merror, [data-mjx-error]')) {
    throw new Error('Unexpected equation');
  }
  const title = article.querySelector('h1')?.textContent.trim();
  if (!title || !document.title.startsWith(`${title} |`)) throw new Error('Title');
  const ids = [...document.querySelectorAll('[id]')].map(node => node.id);
  if (new Set(ids).size !== ids.length) throw new Error('Duplicate IDs');
  const base = document.body.dataset.baseurl;
  const topic = document.querySelector(`.nav-topic[data-topic="${base}/wiki/topics/security/"]`);
  if (!topic?.open || topic.querySelector('.nav-subtopic')) throw new Error('Navigation contract');
  const records = await fetch(`${base}/search.json`).then(response => response.json());
  const book = records.filter(row => new URL(row.url, location.origin).pathname.startsWith(
    `${base}/wiki/topics/security/security-101/`));
  if (book.length !== 14 || new Set(book.map(row => row.url)).size !== 14) throw new Error('Search routes');
  const total = records.filter(row => new URL(row.url, location.origin).pathname.startsWith(
    `${base}/wiki/topics/security/`));
  if (total.length !== 24) throw new Error('Original study missing');
  if (book.find(row => new URL(row.url, location.origin).pathname === location.pathname)?.title !== title) {
    throw new Error('Search title mismatch');
  }
  const pager = document.querySelector('[data-chapter-pagination]');
  if (!pager || pager.hidden || [...pager.querySelectorAll('a')].some(link =>
      !new URL(link.href).pathname.startsWith(`${base}/wiki/topics/security/`))) {
    throw new Error('Chapter pagination');
  }
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth) {
    throw new Error('Horizontal page overflow');
  }
  return {page: location.pathname, viewport: innerWidth, figures: images.length,
    studyPages: book.length, totalSecurityPages: total.length, version: document.body.dataset.indexVersion};
})();
