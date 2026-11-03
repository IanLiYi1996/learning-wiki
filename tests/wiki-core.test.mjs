import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
import test from 'node:test';
const core = createRequire(import.meta.url)('../assets/js/wiki-core.js');
const origin = 'https://example.com';
const data = [
  { title: 'GPU 管线', url: '/learning-wiki/wiki/gpu.html', text: 'Shader 与渲染模型' },
  { title: '材质', url: '/learning-wiki/wiki/material.html', text: 'GPU 管线和 Shader 示例' },
  { title: 'Palantir Ontology', url: '/learning-wiki/wiki/ontology.html', text: '本体对象和业务关系' },
];
test('normalization supports full-width English and whitespace', () => {
  assert.equal(core.normalizeText('ＧＰＵ \n Shader'), 'gpu shader');
  assert.equal(core.normalizeText(null), '');
});
test('canonical routes preserve project prefix and decode UTF8', () => {
  assert.equal(core.canonicalPath('/learning-wiki/wiki/README.html', origin), '/learning-wiki/wiki/');
  assert.equal(core.canonicalPath('/learning-wiki/wiki/index.html?a=1', origin), '/learning-wiki/wiki/');
  assert.equal(core.canonicalPath('/learning-wiki/%E6%95%B0%E6%8D%AE.html', origin), '/learning-wiki/数据.html');
});
test('invalid, external and non-project search records are rejected', () => {
  const records = [...data, null, {}, { ...data[0], url: 'javascript:alert(1)' },
    { ...data[0], url: 'https://other.com/learning-wiki/a.html' },
    { ...data[0], url: '/another-project/a.html' }, { ...data[0], url: 'http://[' }];
  assert.equal(core.prepareDocuments(records, origin, '/learning-wiki/').length, 3);
});
test('README and directory aliases are deduplicated', () => {
  const records = [{ ...data[0], url: '/learning-wiki/wiki/' }, { ...data[0], url: '/learning-wiki/wiki/README.html' }];
  assert.equal(core.prepareDocuments(records, origin, '/learning-wiki/').length, 1);
});
test('malformed URL encoding does not disable valid search records', () => {
  const records = [...data, { ...data[0], url: '/learning-wiki/wiki/%E0%A4.html' }];
  assert.equal(core.prepareDocuments(records, origin, '/learning-wiki/').length, 3);
});
test('validated links remain same-origin with double-slash paths', () => {
  const docs = core.prepareDocuments([{ ...data[0], url: 'https://example.com//outside.example/path' }], origin, '/');
  assert.equal(new URL(docs[0].url, origin).origin, origin);
});
test('title hits precede body-only hits', () => {
  const docs = core.prepareDocuments(data, origin, '/learning-wiki/');
  assert.deepEqual(core.searchDocuments(docs, 'GPU').map(d => d.title), ['GPU 管线', '材质']);
});
test('multi-token searches require every term', () => {
  const docs = core.prepareDocuments(data, origin, '/learning-wiki/');
  assert.equal(core.searchDocuments(docs, 'gpu shader').length, 2);
  assert.equal(core.searchDocuments(docs, 'gpu ontology').length, 0);
});
test('Chinese and empty searches behave predictably', () => {
  const docs = core.prepareDocuments(data, origin, '/learning-wiki/');
  assert.equal(core.searchDocuments(docs, '本体')[0].title, 'Palantir Ontology');
  assert.deepEqual(core.searchDocuments(docs, '  '), []);
  assert.equal(core.searchDocuments(docs, 'gpu', 1).length, 1);
});
test('excerpts stay short and include the matching context', () => {
  const text = '起始 '.repeat(80) + 'Shader' + ' 结尾'.repeat(80);
  assert.match(core.excerpt(text, 'shader'), /Shader/);
  assert.ok(core.excerpt(text, 'shader').length <= 112);
  assert.equal(core.excerpt('', 'gpu'), '');
});
test('reading-time estimates never show zero', () => {
  assert.equal(core.readingMinutes(''), 1);
  assert.equal(core.readingMinutes('文'.repeat(800)), 2);
});
test('chapter neighbors stay in the selected subgroup, not adjacent categories', () => {
  const links = ['data', 'agents', 'rewards'].map(name => ({
    href: `${origin}/learning-wiki/training/${name}.html`, hash: '',
  }));
  const root = { href: `${origin}/learning-wiki/`, hash: '' };
  assert.deepEqual(core.chapterNeighbors(links, links[1].href, root),
    { previous: links[0], next: links[2] });
  assert.deepEqual(core.chapterNeighbors(links, links[0].href, root),
    { previous: root, next: links[1] });
  assert.deepEqual(core.chapterNeighbors(links, links[2].href, root),
    { previous: links[1], next: null });
});
test('a one-page subgroup retains a path back to the topic guide', () => {
  const chapter = { href: `${origin}/learning-wiki/research.html`, hash: '' };
  const root = { href: `${origin}/learning-wiki/`, hash: '' };
  assert.deepEqual(core.chapterNeighbors([chapter], chapter.href, root),
    { previous: root, next: null });
  assert.equal(core.chapterNeighbors([chapter], root.href, root), null);
});
test('fragment leaves and README aliases do not create duplicate chapters', () => {
  const root = { href: `${origin}/learning-wiki/`, hash: '' };
  const alias = { href: `${origin}/learning-wiki/README.html`, hash: '' };
  const chapter = { href: `${origin}/learning-wiki/book.html`, hash: '' };
  const fragment = { href: chapter.href + '#one', hash: '#one' };
  const invalid = { href: 'http://[', hash: '' };
  assert.deepEqual(core.chapterNeighbors([root, alias, fragment, invalid, chapter], chapter.href),
    { previous: root, next: null });
  assert.deepEqual(core.chapterNeighbors([root], alias.href, root),
    { previous: null, next: null });
});
