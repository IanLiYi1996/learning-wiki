// Read-only QA for the original eight recipe pages; named session only.
(async () => {
  // A URL navigation can finish before deferred wiki enhancement scripts.
  if (document.readyState === 'loading') {
    await new Promise(resolve => document.addEventListener('DOMContentLoaded', resolve, { once: true }));
  }
  const article = document.querySelector('.article-content');
  if (!article) throw new Error('Missing training article');
  const route = location.pathname;
  const name = route.split('/').pop() || 'index.html';
  const isHub = route.endsWith('/training/');
  const counts = { 'index.html': 1, 'data-sft-and-rlvr.html': 1,
    'agentic-environments.html': 2, 'reward-and-stability.html': 1,
    'infrastructure-and-evaluation.html': 2, 'lab.html': 1, 'sources.html': 0 };
  const expected = isHub ? 0 : counts[name];
  if (expected === undefined) throw new Error('Unknown training page');
  const title = article.querySelector('h1')?.textContent.trim();
  if (!title || !document.title.startsWith(`${title} |`)) throw new Error('Wrong page title');
  const images = Array.from(article.querySelectorAll('.wiki-figure img'));
  if (images.length !== expected) throw new Error('Wrong figure count');
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
  await window.MathJax.startup.promise;
  if (article.querySelector('mjx-merror, [data-mjx-error]')) throw new Error('Invalid math');
  const ids = Array.from(document.querySelectorAll('[id]'), node => node.id);
  if (new Set(ids).size !== ids.length) throw new Error('Duplicate IDs');
  const topic = document.querySelector('.site-sidebar .nav-topic[open]');
  const groups = Array.from(topic.querySelectorAll('.nav-subtopic'));
  const names = ['LLM 训练与后训练', '扩散与视觉生成', '视觉表征与多模态', '推理与硬件',
    '自动研究与评测', '权重编辑与解释'];
  if (JSON.stringify(groups.map(group => group.dataset.subtopic)) !== JSON.stringify(names)) {
    throw new Error('Incorrect taxonomy');
  }
  const opened = groups.filter(group => group.open);
  if (opened.length !== 1 || opened[0].dataset.subtopic !== names[0]) {
    throw new Error('Current subgroup/ancestors not opened');
  }
  const pagination = document.querySelector('[data-chapter-pagination]');
  if (!pagination || pagination.hidden) throw new Error('Missing group pagination');
  const base = document.body.dataset.baseurl;
  const records = await fetch(`${base}/search.json`).then(response => {
    if (!response.ok) throw new Error('Search unavailable');
    return response.json();
  });
  const study = records.filter(record => new URL(record.url, location.origin).pathname
    .startsWith(`${base}/wiki/topics/deep-learning/training/`));
  if (study.length !== 17 || new Set(study.map(record => record.url)).size !== 17) {
    throw new Error('Expected seventeen searchable training pages');
  }
  if (study.find(record => new URL(record.url, location.origin).pathname === route)?.title !== title) {
    throw new Error('Incorrect search title');
  }
  const neighbors = Array.from(pagination.querySelectorAll('a'), link => new URL(link.href).pathname);
  if (neighbors.some(path => !path.startsWith(`${base}/wiki/topics/deep-learning/training/`) &&
      path !== `${base}/wiki/topics/deep-learning/`)) throw new Error('Cross-group pagination');
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth) {
    throw new Error('Page overflow');
  }
  return { page: route, viewport: innerWidth, figures: images.length,
    equations: article.querySelectorAll('mjx-container').length, searchPages: study.length,
    openedGroup: opened[0].dataset.subtopic, pagination: neighbors,
    version: document.body.dataset.indexVersion };
})();
