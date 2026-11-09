// Read-only checks for nine Agentic-RL Lab pages, desktop and mobile.
(async () => {
  if (document.readyState === 'loading') {
    await new Promise(resolve => document.addEventListener('DOMContentLoaded', resolve, { once: true }));
  }
  const article = document.querySelector('.article-content');
  if (!article) throw new Error('Missing article');
  const counts = { 'index.html': 2, 'policy-objectives.html': 2,
    'tools-and-environments.html': 1, 'on-policy-distillation.html': 1,
    'credit-assignment.html': 1, 'multimodal-and-judges.html': 1,
    'evaluation-and-reproduction.html': 1, 'lab.html': 1, 'sources.html': 0 };
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
  const topic = document.querySelector('.nav-topic[open]');
  const groups = Array.from(topic.querySelectorAll('.nav-subtopic'));
  const names = ['LLM 训练与后训练', '扩散与视觉生成', '视觉表征与多模态', '实时全双工交互', '推理与硬件',
    '自动研究与评测', '权重编辑与解释'];
  if (JSON.stringify(groups.map(g => g.dataset.subtopic)) !== JSON.stringify(names)) {
    throw new Error('Taxonomy changed');
  }
  if (groups.filter(g => g.open).length !== 1 || !groups[0].open) throw new Error('Current group closed');
  const base = document.body.dataset.baseurl;
  const records = await fetch(`${base}/search.json`).then(r => {
    if (!r.ok) throw new Error('Search failed');
    return r.json();
  });
  const study = records.filter(r => new URL(r.url, location.origin).pathname.startsWith(
    `${base}/wiki/topics/deep-learning/training/agentic-rl-lab/`));
  if (study.length !== 9 || new Set(study.map(r => r.url)).size !== 9) throw new Error('Search count');
  if (study.find(r => new URL(r.url, location.origin).pathname === location.pathname)?.title !== title) {
    throw new Error('Search title mismatch');
  }
  const pagination = document.querySelector('[data-chapter-pagination]');
  if (!pagination || pagination.hidden) throw new Error('No pagination');
  const neighbors = Array.from(pagination.querySelectorAll('a'), a => new URL(a.href).pathname);
  if (neighbors.some(p => !p.startsWith(`${base}/wiki/topics/deep-learning/training/`))) {
    throw new Error('Cross-group pagination');
  }
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth) {
    throw new Error('Horizontal page overflow');
  }
  return { page: location.pathname, viewport: innerWidth, figures: images.length,
    equations: article.querySelectorAll('mjx-container').length, searchPages: study.length,
    pagination: neighbors, version: document.body.dataset.indexVersion };
})();
