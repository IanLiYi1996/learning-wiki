// Read-only checks for the 22 memory/continuous-generation pages.
// Run with agent-browser eval --stdin after opening a locally built page.
(async () => {
  if (document.readyState === 'loading') {
    await new Promise(resolve => document.addEventListener('DOMContentLoaded', resolve, { once: true }));
  }
  const base = document.body.dataset.baseurl;
  const memoryRoot = `${base}/wiki/topics/agent-memory/`;
  const flowRoot = `${base}/wiki/topics/deep-learning/continuous-language-models/`;
  const memory = location.pathname.startsWith(memoryRoot);
  const root = memory ? memoryRoot : flowRoot;
  const path = location.pathname.slice(root.length) || 'index.html';
  const displays = memory ? {
    'index.html': 0,
    '01-memory-and-state.html': 1,
    '02-write-manage-read.html': 0,
    '03-representations-and-retrieval.html': 0,
    '04-evaluation-and-ablation.html': 2,
    '05-safety-and-governance.html': 0,
    '06-anthropic-components.html': 0,
    'glossary.html': 0,
    'lab.html': 0,
    'sources.html': 0,
  } : {
    'index.html': 0,
    '01-discrete-text-continuous-state.html': 2,
    '02-representations-and-decoders.html': 2,
    '03-diffusion-and-flow-matching.html': 3,
    '04-training-schedules-and-self-conditioning.html': 2,
    '05-sampling-guidance-and-commitment.html': 1,
    '06-flow-maps-and-few-step-generation.html': 2,
    '07-scaling-and-evaluation.html': 1,
    '08-safety-and-research-roadmap.html': 0,
    'glossary.html': 0,
    'lab.html': 0,
    'sources.html': 0,
  };
  if (!location.pathname.startsWith(root) || !Object.hasOwn(displays, path)) {
    throw new Error('Unknown memory/flow page');
  }
  const article = document.querySelector('.article-content');
  const title = article?.querySelector('h1')?.textContent.trim();
  if (!title || !document.title.startsWith(`${title} |`)) throw new Error('Page title');
  await window.MathJax.startup.promise;
  if (article.querySelector('mjx-merror, [data-mjx-error]')) throw new Error('Invalid math');
  const equations = article.querySelectorAll('mjx-container[display="true"]').length;
  if (equations !== displays[path]) throw new Error(`Display math: ${equations}/${displays[path]}`);
  const ids = [...document.querySelectorAll('[id]')].map(node => node.id);
  if (new Set(ids).size !== ids.length) throw new Error('Duplicate IDs');
  const topics = [...document.querySelectorAll('.site-sidebar .nav-topic[open]')];
  const topicRoot = memory ? root : `${base}/wiki/topics/deep-learning/`;
  if (topics.length !== 1 || topics[0].dataset.topic !== topicRoot) {
    throw new Error('Wrong open topic');
  }
  const active = [...topics[0].querySelectorAll('.nav-leaf[aria-current="page"]')];
  if (active.length !== 1 || new URL(active[0].href).pathname !== location.pathname) {
    throw new Error('Active chapter');
  }
  const groups = [...topics[0].querySelectorAll('.nav-subtopic')];
  const openedGroups = groups.filter(group => group.open);
  if (memory ? groups.length !== 0 :
      groups.length !== 7 || openedGroups.length !== 1 ||
      openedGroups[0].dataset.subtopic !== '扩散与生成模型') {
    throw new Error('Current subgroup');
  }
  const toc = [...document.querySelectorAll('[data-toc] a')];
  const headings = article.querySelectorAll('h2[id], h3[id]');
  if (toc.length !== headings.length ||
      toc.some(link => !document.getElementById(decodeURIComponent(link.hash.slice(1))))) {
    throw new Error('Page outline');
  }
  const pager = document.querySelector('[data-chapter-pagination]');
  if (!pager || pager.hidden) throw new Error('Missing chapter navigation');
  const scope = memory ? topics[0] : openedGroups[0];
  const allowed = new Set([...scope.querySelectorAll('.nav-leaf')]
    .map(link => new URL(link.href).pathname));
  allowed.add(topicRoot);
  const neighbors = [...pager.querySelectorAll('a')].map(link => new URL(link.href).pathname);
  if (neighbors.some(route => !allowed.has(route))) throw new Error('Cross-group neighbor');
  const records = await fetch(`${base}/search.json`).then(response => {
    if (!response.ok) throw new Error('Search index response');
    return response.json();
  });
  const selected = records.filter(row => new URL(row.url, location.origin).pathname.startsWith(root));
  const expected = Object.keys(displays).length;
  if (selected.length !== expected || new Set(selected.map(row => row.url)).size !== expected) {
    throw new Error('Search scope');
  }
  if (!selected.some(row => row.title === title &&
      new URL(row.url, location.origin).pathname === location.pathname)) {
    throw new Error('Search title or route');
  }
  const markdownLinks = [...article.querySelectorAll('a[href]')].some(link => {
    const url = new URL(link.href);
    return url.origin === location.origin && url.pathname.endsWith('.md');
  });
  if (markdownLinks ||
      /\]\([^)]*\.md/.test(article.innerText)) throw new Error('Markdown link leak');
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth) {
    throw new Error('Horizontal document overflow');
  }
  return { page: location.pathname, viewport: innerWidth, displayEquations: equations,
    searchPages: selected.length, toc: toc.length, neighbors };
})();
