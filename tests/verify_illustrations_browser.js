// Run against the local Jekyll preview:
// agent-browser --session wiki-figures eval --stdin < tests/verify_illustrations_browser.js
(async () => {
  const base = document.body.dataset.baseurl;
  const indexResponse = await fetch(base + '/search.json');
  if (!indexResponse.ok) throw new Error('Search index did not load');
  const index = await indexResponse.json();
  const routes = [...new Set(index.map(record => record.url))];
  const assets = new Set();
  const failures = [];
  let illustratedPages = 0, placements = 0;
  await Promise.all(routes.map(async route => {
    const response = await fetch(route);
    if (!response.ok) throw new Error('Page failed: ' + route);
    const parsed = new DOMParser().parseFromString(await response.text(), 'text/html');
    const images = [...parsed.querySelectorAll('img[src]')]
      .filter(image => /\/wiki\/topics\/[^/]+\/images\/[^/]+\.png$/.test(image.getAttribute('src')));
    if (!images.length) return;
    illustratedPages++;
    placements += images.length;
    if (!parsed.querySelector('script[src*="wiki-figures.js"]')) {
      failures.push({ route, reason: 'Missing progressive enhancement' });
    }
    images.forEach(image => {
      const url = new URL(image.getAttribute('src'), location.origin);
      if (url.origin !== location.origin) throw new Error('External image: ' + url.href);
      assets.add(url.href.replace(/\.png$/, '.svg'));
    });
  }));
  await document.fonts.ready;
  for (const asset of assets) {
    const response = await fetch(asset);
    if (!response.ok) {
      failures.push({ asset, reason: 'SVG not reachable' });
      continue;
    }
    const xml = new DOMParser().parseFromString(await response.text(), 'image/svg+xml');
    if (xml.querySelector('parsererror')) throw new Error('Invalid SVG: ' + asset);
    const svg = document.importNode(xml.documentElement, true);
    svg.style.position = 'absolute';
    svg.style.left = '-20000px';
    svg.style.visibility = 'hidden';
    svg.setAttribute('aria-hidden', 'true');
    document.body.append(svg);
    const width = Number(svg.getAttribute('width')), height = Number(svg.getAttribute('height'));
    svg.querySelectorAll('text').forEach(text => {
      const box = text.getBBox();
      if (box.x < 0 || box.y < 0 || box.x + box.width > width
        || box.y + box.height > height) {
        failures.push({ asset, reason: 'Text outside canvas', text: text.textContent });
      }
    });
    svg.remove();
  }
  const report = { illustratedPages, placements, uniqueSVGs: assets.size, failures };
  if (illustratedPages < 67 || placements < 143 || assets.size < 83) {
    throw new Error('Missing coverage: ' + JSON.stringify(report));
  }
  if (failures.length) throw new Error(JSON.stringify(report));
  return report;
})();
