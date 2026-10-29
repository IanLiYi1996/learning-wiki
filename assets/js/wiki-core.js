(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.WikiCore = api;
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  function normalizeText(value) {
    return String(value || '').normalize('NFKC').toLocaleLowerCase().replace(/\s+/g, ' ').trim();
  }
  function canonicalPath(value, origin) {
    return decodeURI(new URL(value, origin || 'https://wiki.invalid').pathname)
      .replace(/\/(?:index|README)\.html$/i, '/');
  }
  function prepareDocuments(records, origin, basePath) {
    const documents = new Map();
    for (const record of records) {
      if (!record || typeof record.title !== 'string' || typeof record.url !== 'string'
        || typeof record.text !== 'string') continue;
      let url;
      try { url = new URL(record.url, origin); } catch (_) { continue; }
      if (url.origin !== new URL(origin).origin || !url.pathname.startsWith(basePath)) continue;
      let key;
      try { key = canonicalPath(url.href); } catch (_) { continue; }
      if (!documents.has(key)) documents.set(key, {
        title: record.title, text: record.text, url: url.href,
        searchTitle: normalizeText(record.title), searchText: normalizeText(record.text),
      });
    }
    return Array.from(documents.values());
  }
  function searchDocuments(documents, query, limit) {
    const terms = normalizeText(query).split(' ').filter(Boolean);
    if (!terms.length) return [];
    return documents.map(doc => {
      if (!terms.every(term => doc.searchTitle.includes(term) || doc.searchText.includes(term))) return null;
      const score = terms.reduce((total, term) => total
        + (doc.searchTitle === term ? 100 : doc.searchTitle.startsWith(term) ? 60
          : doc.searchTitle.includes(term) ? 30 : 3), 0);
      return { doc, score };
    }).filter(Boolean).sort((a, b) => b.score - a.score || a.doc.title.localeCompare(b.doc.title))
      .slice(0, limit || 12).map(result => result.doc);
  }
  function excerpt(text, query, length) {
    const source = String(text || '').replace(/\s+/g, ' ').trim();
    const terms = normalizeText(query).split(' ').filter(Boolean);
    const normalized = normalizeText(source);
    const hit = terms.map(term => normalized.indexOf(term)).filter(index => index >= 0)
      .sort((a, b) => a - b)[0] || 0;
    const start = Math.max(0, hit - 32), size = length || 110;
    return (start ? '…' : '') + source.slice(start, start + size)
      + (source.length > start + size ? '…' : '');
  }
  function readingMinutes(text) {
    const han = (String(text).match(/[\u3400-\u9fff]/g) || []).length;
    const words = (String(text).replace(/[\u3400-\u9fff]/g, ' ').match(/[a-zA-Z0-9]+/g) || []).length;
    return Math.max(1, Math.ceil(han / 400 + words / 180));
  }
  return { normalizeText, canonicalPath, prepareDocuments, searchDocuments, excerpt, readingMinutes };
});
