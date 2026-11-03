// Read-only QA on a built weight-space article, at the selected viewport.
// agent-browser --session <isolated-session> eval --stdin < tests/verify_weight_space_browser.js
(async () => {
  const article = document.querySelector('.article-content');
  if (!article) throw new Error('Missing wiki article');
  const path = location.pathname;
  const isBook = path.endsWith('/weight-space-programming.html');
  const isLab = path.endsWith('/weight-space-programming-lab.html');
  const expectedFigures = isBook ? 9 : isLab ? 1 : 0;
  const images = Array.from(article.querySelectorAll('.wiki-figure img'));
  if (images.length !== expectedFigures) throw new Error('Wrong enhanced figure count');
  for (const image of images) {
    image.loading = 'eager';
    await image.decode();
    if (!image.naturalWidth || !image.alt || !image.closest('figure').querySelector('figcaption')) {
      throw new Error('Missing figure content or description');
    }
    if (new URL(image.currentSrc).origin !== location.origin ||
        !new URL(image.currentSrc).pathname.endsWith('.svg')) {
      throw new Error('Expected same-origin SVG with portable PNG fallback');
    }
  }
  let mathCount = 0;
  if (isBook) {
    if (!window.MathJax?.startup?.promise) throw new Error('Math renderer unavailable');
    await window.MathJax.startup.promise;
    mathCount = article.querySelectorAll('mjx-container').length;
    if (mathCount < 10 || article.querySelector('mjx-merror, [data-mjx-error]')) {
      throw new Error('Incomplete or invalid typeset equations');
    }
    for (let number = 1; number <= 10; number++) {
      if (!article.querySelector(`#wsp-${String(number).padStart(2, '0')}`)) {
        throw new Error('Missing explicit lesson anchor');
      }
    }
  }
  const ids = Array.from(document.querySelectorAll('[id]'), node => node.id);
  if (new Set(ids).size !== ids.length) throw new Error('Duplicate page IDs');
  const base = document.body.dataset.baseurl;
  const records = await fetch(`${base}/search.json`).then(response => {
    if (!response.ok) throw new Error('Search index unavailable');
    return response.json();
  });
  const topic = `${base}/wiki/topics/deep-learning/`;
  const study = records.filter(record => {
    const route = new URL(record.url, location.origin).pathname;
    return route.startsWith(topic) && !route.slice(topic.length).includes('/');
  });
  if (study.length !== 5 || new Set(study.map(record => record.url)).size !== 5) {
    throw new Error('Expected five searchable topic pages');
  }
  const pagination = document.querySelector('[data-chapter-pagination]');
  if (!pagination || pagination.hidden) throw new Error('Missing topic pagination');
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth) {
    throw new Error('Horizontal page overflow');
  }
  return {
    page: path.split('/').pop() || 'index',
    decodedFigures: images.length,
    typesetEquations: mathCount,
    searchablePages: study.length,
    pagination: Array.from(pagination.querySelectorAll('a'), link => new URL(link.href).pathname),
    viewport: innerWidth,
    overflow: false,
  };
})();
