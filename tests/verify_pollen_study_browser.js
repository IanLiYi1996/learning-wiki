// Read-only checks for the nine additive pages; named browser session required.
(async () => {
  if (document.readyState === 'loading') {
    await new Promise(resolve => document.addEventListener('DOMContentLoaded', resolve, { once: true }));
  }
  const article = document.querySelector('.article-content');
  if (!article || article.querySelector('[data-physical-reader]')) throw new Error('Wrong study layout');
  const counts = { 'index.html': 2, 'robots-and-sdk.html': 1,
    'teleoperation-and-logging.html': 1, 'perception-and-simulation.html': 2,
    'data-and-policy-learning.html': 1, 'microduck-and-rl.html': 1,
    'hands-and-actuators.html': 1, 'lab.html': 1, 'sources.html': 0 };
  const name = location.pathname.split('/').pop() || 'index.html';
  if (counts[name] === undefined) throw new Error('Unknown page');
  const title = article.querySelector('h1')?.textContent.trim();
  if (!title || !document.title.startsWith(`${title} |`)) throw new Error('Title mismatch');
  const images = Array.from(article.querySelectorAll('.wiki-figure img'));
  if (images.length !== counts[name]) throw new Error('Figure count mismatch');
  for (const image of images) {
    image.loading = 'eager';
    await image.decode();
    if (!image.naturalWidth || !image.alt ||
        !image.closest('figure').querySelector('figcaption')) throw new Error('Bad figure');
    const asset = new URL(image.currentSrc);
    if (asset.origin !== location.origin || !asset.pathname.endsWith('.svg')) {
      throw new Error('Missing local SVG enhancement');
    }
  }
  await window.MathJax.startup.promise;
  if (article.querySelector('mjx-merror, [data-mjx-error]')) throw new Error('Invalid equation');
  const ids = Array.from(document.querySelectorAll('[id]'), node => node.id);
  if (new Set(ids).size !== ids.length) throw new Error('Duplicate IDs');
  const base = document.body.dataset.baseurl;
  const currentTopic = document.querySelector(`.nav-topic[data-topic="${base}/wiki/topics/physical-ai/"]`);
  if (!currentTopic?.open || currentTopic.querySelector('.nav-subtopic')) {
    throw new Error('Physical AI navigation changed unexpectedly');
  }
  const records = await fetch(`${base}/search.json`).then(response => {
    if (!response.ok) throw new Error('Search failed');
    return response.json();
  });
  const study = records.filter(record => new URL(record.url, location.origin).pathname.startsWith(
    `${base}/wiki/topics/physical-ai/pollen-robotics/`));
  if (study.length !== 9 || new Set(study.map(r => r.url)).size !== 9) throw new Error('Search count');
  if (study.find(r => new URL(r.url, location.origin).pathname === location.pathname)?.title !== title) {
    throw new Error('Search title mismatch');
  }
  const pagination = document.querySelector('[data-chapter-pagination]');
  if (!pagination || pagination.hidden) throw new Error('Missing pagination');
  const neighbors = Array.from(pagination.querySelectorAll('a'), link => new URL(link.href).pathname);
  if (neighbors.some(path => !path.startsWith(`${base}/wiki/topics/physical-ai/`))) {
    throw new Error('Cross-topic pagination');
  }
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth) {
    throw new Error('Horizontal page overflow');
  }
  return { page: location.pathname, viewport: innerWidth, figures: images.length,
    equations: article.querySelectorAll('mjx-container').length, searchPages: study.length,
    pagination: neighbors, version: document.body.dataset.indexVersion };
})();
