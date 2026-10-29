(function () {
  'use strict';
  const article = document.querySelector('.article-content');
  if (!article) return;
  const images = Array.from(article.querySelectorAll('img')).filter(image => {
    const url = new URL(image.src, location.href);
    return url.origin === location.origin
      && /\/wiki\/topics\/[^/]+\/images\/[^/]+\.png$/.test(url.pathname);
  });
  if (!images.length) return;

  const dialog = document.createElement('dialog');
  dialog.className = 'diagram-dialog';
  dialog.setAttribute('aria-labelledby', 'diagram-title');
  const toolbar = document.createElement('div');
  toolbar.className = 'diagram-toolbar';
  const title = document.createElement('h2');
  title.id = 'diagram-title';
  const zoom = document.createElement('button');
  zoom.type = 'button';
  zoom.textContent = '原尺寸';
  zoom.setAttribute('aria-pressed', 'false');
  const download = document.createElement('a');
  download.textContent = 'PNG';
  download.setAttribute('download', '');
  const close = document.createElement('button');
  close.type = 'button';
  close.textContent = '关闭';
  close.setAttribute('aria-label', '关闭大图');
  toolbar.append(title, zoom, download, close);
  const stage = document.createElement('div');
  stage.className = 'diagram-stage';
  stage.tabIndex = 0;
  stage.setAttribute('aria-label', '图解；原尺寸模式可滚动查看');
  const fullImage = document.createElement('img');
  fullImage.className = 'diagram-full-image';
  stage.append(fullImage);
  dialog.append(toolbar, stage);
  document.body.append(dialog);

  let opener = null;
  let fallback = '';
  fullImage.addEventListener('error', () => {
    if (fallback && fullImage.src !== fallback) fullImage.src = fallback;
  });
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    document.body.classList.remove('diagram-is-open');
    if (opener) opener.focus({ preventScroll: true });
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right
      || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });
  zoom.addEventListener('click', () => {
    const enlarged = dialog.classList.toggle('diagram-native-size');
    zoom.setAttribute('aria-pressed', String(enlarged));
    zoom.textContent = enlarged ? '适应窗口' : '原尺寸';
  });

  images.forEach(image => {
    const png = image.src;
    const svg = new URL(png);
    svg.pathname = svg.pathname.replace(/\.png$/, '.svg');
    const picture = document.createElement('picture');
    const source = document.createElement('source');
    source.type = 'image/svg+xml';
    source.srcset = svg.href;
    // Source failure falls back to the original portable PNG, not a broken icon.
    image.addEventListener('error', () => source.remove(), { once: true });
    image.loading = 'lazy';
    image.decoding = 'async';
    const link = document.createElement('a');
    link.className = 'diagram-open';
    link.href = svg.href;
    const label = image.alt.split('。')[0] || '学习图解';
    link.setAttribute('aria-label', `查看大图：${label}`);
    link.title = '点击查看大图';
    const figure = document.createElement('figure');
    figure.className = 'wiki-figure';
    const paragraph = image.parentElement;
    const captionParagraph = paragraph.nextElementSibling;
    const standalone = paragraph.tagName === 'P'
      && paragraph.children.length === 1 && !paragraph.textContent.trim();
    if (standalone) paragraph.replaceWith(figure);
    else image.replaceWith(figure);
    picture.append(source, image);
    link.append(picture);
    figure.append(link);
    const caption = document.createElement('figcaption');
    if (standalone && captionParagraph && captionParagraph.tagName === 'P'
      && captionParagraph.textContent.trim().startsWith('图：')) {
      caption.textContent = captionParagraph.textContent;
      captionParagraph.remove();
    } else caption.textContent = `图：${label}`;
    const hint = document.createElement('span');
    hint.className = 'diagram-hint';
    hint.textContent = '点击放大';
    caption.append(hint);
    figure.append(caption);
    link.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      if (typeof dialog.showModal !== 'function') return; // SVG link still works.
      event.preventDefault();
      opener = link;
      title.textContent = label;
      fullImage.alt = image.alt;
      fallback = png;
      fullImage.src = svg.href;
      download.href = png;
      dialog.classList.remove('diagram-native-size');
      zoom.setAttribute('aria-pressed', 'false');
      zoom.textContent = '原尺寸';
      stage.scrollTop = stage.scrollLeft = 0;
      dialog.showModal();
      document.body.classList.add('diagram-is-open');
      close.focus();
    });
  });
})();
