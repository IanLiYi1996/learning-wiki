// Run on any extension chapter after the normal wiki scripts have loaded:
// agent-browser --session <isolated-session> eval --stdin < tests/verify_payments_browser.js
(async () => {
  const slugs = [
    '13-card-products-and-operations',
    '14-in-person-and-offline-payments',
    '15-recurring-payments',
    '16-merchant-lifecycle',
    '17-treasury-and-liquidity',
    '18-messages-and-payment-security',
    '19-ledgers-and-reliable-payment-engineering',
    '20-china-and-regulatory-maps',
    '21-cash-mobile-money-and-local-methods',
    '22-cbdc-tokenised-deposits-and-stablecoins',
  ];
  const imageCounts = [2, 2, 1, 2, 2, 2, 2, 2, 1, 2];
  const article = document.querySelector('.article-content');
  const match = article?.querySelector('h1')?.textContent.match(/^(\d{2}) /);
  const number = Number(match?.[1]);
  const index = number - 13;
  if (index < 0 || index >= slugs.length || !Number.isInteger(index)) {
    throw new Error('Expected an extension chapter (13–22)');
  }
  if (!article.querySelector(`#lesson-${number}`) || !article.querySelector('#public-sources')) {
    throw new Error('Missing explicit lesson or bibliography anchor');
  }
  const images = Array.from(article.querySelectorAll('figure.wiki-figure img'));
  if (images.length !== imageCounts[index]) throw new Error('Wrong enhanced figure count');
  for (const image of images) {
    image.loading = 'eager';
    await image.decode();
    if (!image.naturalWidth || !image.alt.trim()) throw new Error('Undecodable/unnamed figure');
    if (!image.currentSrc.endsWith('.svg')) throw new Error('Missing local SVG enhancement');
    const figure = image.closest('figure');
    if (!figure.querySelector('figcaption')?.textContent.includes('图：')) {
      throw new Error('Missing figure caption');
    }
    const svg = figure.querySelector('.diagram-open');
    if (!svg || new URL(svg.href).origin !== location.origin) {
      throw new Error('Figure viewer is not a same-origin local link');
    }
  }
  const pagination = document.querySelector('[data-chapter-pagination]');
  const actual = Array.from(pagination.querySelectorAll('a'), a => new URL(a.href).pathname);
  const base = document.body.dataset.baseurl;
  const prefix = `${base}/wiki/topics/payments/`;
  const previous = index ? `chapters/${slugs[index - 1]}.html` : 'payment-industry-101.html';
  const next = index < slugs.length - 1 ? `chapters/${slugs[index + 1]}.html` : 'glossary.html';
  if (pagination.hidden || actual.join('|') !== [prefix + previous, prefix + next].join('|')) {
    throw new Error('Wrong previous/next chapter links');
  }
  const records = await fetch(`${base}/search.json`).then(response => {
    if (!response.ok) throw new Error('Search index unavailable');
    return response.json();
  });
  const payments = records.filter(record => new URL(record.url, location.origin).pathname.startsWith(prefix));
  const urls = payments.map(record => new URL(record.url, location.origin).pathname);
  if (urls.length !== 15 || new Set(urls).size !== 15) {
    throw new Error('Search should contain 15 unique payment pages');
  }
  for (const slug of slugs) {
    if (!urls.includes(`${prefix}chapters/${slug}.html`)) {
      throw new Error(`Unsearchable chapter: ${slug}`);
    }
  }
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth) {
    throw new Error('Page has horizontal overflow');
  }
  return { chapter: number, decodedFigures: images.length, searchablePages: urls.length,
    pagination: actual, viewport: innerWidth, overflow: false };
})();
