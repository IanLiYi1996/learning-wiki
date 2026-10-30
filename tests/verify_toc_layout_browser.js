// Run on a built article with headings, after choosing the viewport:
// agent-browser --session wiki-toc-fix eval --stdin < tests/verify_toc_layout_browser.js
(() => {
  const toc = document.querySelector('.page-toc');
  const article = document.querySelector('.article-content');
  const mobile = document.querySelector('[data-mobile-toc]');
  if (!toc || !article || !mobile) throw new Error('Expected wiki article layout');
  const box = toc.getBoundingClientRect();
  const articleBox = article.getBoundingClientRect();
  // CSSOM View: root clientWidth measures the usable viewport without scrollbars.
  const usableWidth = document.documentElement.clientWidth;
  const visible = getComputedStyle(toc).display !== 'none' && !toc.hidden;
  const report = {
    width: innerWidth,
    usableWidth,
    tocVisible: visible,
    tocLeft: box.left,
    tocRight: box.right,
    rightGap: usableWidth - box.right,
    articleRight: articleBox.right,
    articleWidth: articleBox.width,
    mobileTocVisible: getComputedStyle(mobile).display !== 'none' && !mobile.hidden,
    overflow: document.documentElement.scrollWidth > usableWidth,
  };
  const failures = [];
  if (matchMedia('(min-width: 1280px)').matches) {
    if (!visible) failures.push('Desktop table of contents is missing');
    if (visible && (report.rightGap < -1 || report.rightGap > 48)) {
      failures.push(`Table of contents is not at the viewport right edge: ${report.rightGap}px gap`);
    }
    if (visible && box.left < articleBox.right + 15) {
      failures.push('Table of contents overlaps or crowds the article');
    }
    if (articleBox.width > 761) failures.push('Article lost its readable width limit');
  } else if (visible) {
    failures.push('Desktop table of contents should collapse on a narrow viewport');
  } else if (!report.mobileTocVisible) {
    failures.push('The collapsed table of contents is unavailable');
  }
  if (report.overflow) failures.push('Page has horizontal overflow');
  if (failures.length) throw new Error(JSON.stringify({ ...report, failures }));
  return report;
})();
