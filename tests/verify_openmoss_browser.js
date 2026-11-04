// Run with agent-browser eval --stdin on a local built OpenMOSS page.
(async () => {
  const article = document.querySelector('.article-content');
  if (!article) throw new Error('Missing article');
  const base = document.body.dataset.baseurl;
  const root = `${base}/wiki/topics/deep-learning/openmoss/`;
  if (!location.pathname.startsWith(root)) throw new Error('Wrong topic');
  const path = location.pathname.slice(root.length) || 'index.html';
  const displays = {
    'index.html': 0,
    'learning-roadmap.html': 0,
    '01-audio-representation-and-generation.html': 9,
    '02-streaming-video-time-and-cache.html': 0,
    '03-audiovisual-latents-and-joint-denoising.html': 0,
    '04-image-layout-supervision-and-specification.html': 0,
    '05-world-action-and-embodied-agent.html': 2,
    '06-agent-memory-and-executable-evaluation.html': 8,
    '07-long-context-and-diffusion-optimization.html': 4,
    '08-mechanistic-interpretability.html': 10,
    '09-foundation-and-omni-models.html': 1,
    '10-audio-understanding-and-transcription.html': 3,
    '11-robotics-policy-and-control.html': 1,
    '12-honesty-and-long-context-safety.html': 6,
    '13-diffusion-language-models.html': 3,
    '14-post-training-and-rl.html': 8,
    'sources.html': 0,
  };
  if (!Object.hasOwn(displays, path)) throw new Error('Unknown topic route');
  await window.MathJax.startup.promise;
  if (article.querySelector('mjx-merror, [data-mjx-error]')) throw new Error('Invalid math');
  const equations = article.querySelectorAll('mjx-container[display="true"]').length;
  if (equations !== displays[path]) throw new Error(`Display math: ${equations}/${displays[path]}`);
  const title = article.querySelector('h1')?.textContent.trim();
  if (!title || !document.title.startsWith(`${title} |`)) throw new Error('Page title');
  const ids = [...document.querySelectorAll('[id]')].map(node => node.id);
  if (ids.length !== new Set(ids).size) throw new Error('Duplicate anchors');
  const topics = [...document.querySelectorAll('.site-sidebar .nav-topic[open]')];
  if (topics.length !== 1 || topics[0].dataset.topic !== root) {
    throw new Error('Parent topic takes over child navigation');
  }
  const toc = [...document.querySelectorAll('[data-toc] a')];
  if (!toc.length) throw new Error('Missing page TOC');
  for (const link of toc) {
    if (!document.getElementById(decodeURIComponent(link.hash.slice(1)))) throw new Error('TOC target');
  }
  const pager = document.querySelector('[data-chapter-pagination]');
  if (!pager || pager.hidden) throw new Error('Missing chapter navigation');
  const neighbors = [...pager.querySelectorAll('a')].map(link => new URL(link.href).pathname);
  if (neighbors.some(url => !url.startsWith(root))) throw new Error('Cross-topic chapter neighbor');
  const records = await fetch(`${base}/search.json`).then(response => {
    if (!response.ok) throw new Error('Search index response');
    return response.json();
  });
  const selected = records.filter(row => new URL(row.url, location.origin).pathname.startsWith(root));
  if (selected.length !== 17) throw new Error(`Search scope: ${selected.length}`);
  if (!selected.some(row => row.title === title &&
      new URL(row.url, location.origin).pathname === location.pathname)) {
    throw new Error('Search title or route');
  }
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth) {
    throw new Error('Horizontal document overflow');
  }
  return {page: location.pathname, viewport: innerWidth, displayEquations: equations,
    searchPages: selected.length, toc: toc.length, neighbors};
})();
