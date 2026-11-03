// Read-only browser QA: evaluate after opening one collection page.
(async () => {
  const article = document.querySelector('.article-content');
  if (!article) throw new Error('Missing collection article');
  const name = location.pathname.split('/').pop() || 'index.html';
  const title = article.querySelector('h1')?.textContent.trim();
  if (!title || !document.title.startsWith(`${title} |`)) {
    throw new Error('Article title was not recognized in page metadata');
  }
  const expected = {
    'index.html': 1, '01-dpo-and-preference-pairs.html': 1,
    '02-rl-through-denoising.html': 2, '03-rewards-judges-and-advantages.html': 2,
    '04-autoresearch-and-oracles.html': 2, '05-gpu-and-memory-roofline.html': 2,
    '06-realtime-video-estimates.html': 3, 'lab.html': 0,
  };
  if (!(name in expected)) throw new Error(`Unknown collection page: ${name}`);
  const images = Array.from(article.querySelectorAll('.wiki-figure img'));
  if (images.length !== expected[name]) throw new Error(`Wrong figure count on ${name}`);
  for (const image of images) {
    image.loading = 'eager';
    await image.decode();
    if (!image.naturalWidth || !image.alt ||
        !image.closest('figure').querySelector('figcaption')) throw new Error('Bad figure');
    const target = new URL(image.currentSrc);
    if (target.origin !== location.origin || !target.pathname.endsWith('.svg')) {
      throw new Error('Expected local SVG with PNG fallback');
    }
  }
  if (!window.MathJax?.startup?.promise) throw new Error('Math renderer unavailable');
  await window.MathJax.startup.promise;
  const mathCount = article.querySelectorAll('mjx-container').length;
  if (article.querySelector('mjx-merror, [data-mjx-error]')) throw new Error('Invalid equation');
  if (['01-', '02-', '03-', '05-', '06-', 'lab'].some(prefix => name.startsWith(prefix)) &&
      mathCount < 2) throw new Error(`Missing typeset equations on ${name}`);
  const ids = Array.from(document.querySelectorAll('[id]'), node => node.id);
  if (new Set(ids).size !== ids.length) throw new Error('Duplicate IDs');
  if (!article.querySelector('#public-sources')) throw new Error('Missing sources');
  const base = document.body.dataset.baseurl;
  const records = await fetch(`${base}/search.json`).then(response => {
    if (!response.ok) throw new Error('Search unavailable');
    return response.json();
  });
  const collection = `${base}/wiki/topics/deep-learning/diffusion/`;
  const selected = records.filter(record =>
    new URL(record.url, location.origin).pathname.startsWith(collection));
  if (selected.length !== 8 || new Set(selected.map(record => record.url)).size !== 8) {
    throw new Error('Expected eight unique searchable collection pages');
  }
  const record = selected.find(item =>
    new URL(item.url, location.origin).pathname === location.pathname);
  if (!record || record.title !== title) throw new Error('Missing correct search title');
  const pagination = document.querySelector('[data-chapter-pagination]');
  if (!pagination || pagination.hidden) throw new Error('Missing pagination');
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth) {
    throw new Error('Horizontal page overflow');
  }
  return {
    page: name, decodedFigures: images.length, typesetEquations: mathCount,
    searchablePages: selected.length, viewport: innerWidth, overflow: false,
    pagination: Array.from(pagination.querySelectorAll('a'), link => new URL(link.href).pathname),
    indexVersion: document.body.dataset.indexVersion,
  };
})();
