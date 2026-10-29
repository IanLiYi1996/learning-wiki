# frozen_string_literal: true

# Generate native-Jekyll-compatible reading fragments from the existing books.
# No custom Jekyll plugin, duplicated Markdown, remote fetch or archive rewrite.
require 'digest'
require 'json'
require 'pathname'
require 'yaml'
require 'kramdown'
require 'kramdown-parser-gfm'
require 'nokogiri'
require 'addressable/uri'

ROOT = Pathname.new(__dir__).parent
BOOK_ROOT = 'wiki/topics/physical-ai'
BOOKS = [
  { 'key' => 'knowledge', 'label' => '知识全景', 'title' => '知识全景与学习指南',
    'file' => 'Physical_AI_知识全景与学习指南.md' },
  { 'key' => 'industry', 'label' => '业界产品', 'title' => '业界产品与端到端方案',
    'file' => 'industry/Physical_AI_业界产品与端到端方案.md' },
  { 'key' => 'advanced', 'label' => '底层原理', 'title' => '底层原理与实现细节',
    'file' => 'advanced/Physical_AI_底层原理与实现细节.md' },
  { 'key' => 'gtc', 'label' => 'GTC 资料', 'title' => 'GTC Berlin 2026 内容整理',
    'file' => 'conferences/gtc-berlin-2026/GTC_Berlin_2026_Physical_AI_深度调研报告.md' }
].freeze
PROJECT_URLS = {}

def project_url(path)
  # Leave the project prefix to Jekyll, including deployments at the domain root.
  encoded = Addressable::URI.new(path: path).normalize.to_s
  marker = "PHYSICALREADERURL#{Digest::SHA256.hexdigest(encoded)[0, 20]}Z"
  PROJECT_URLS[marker] = "{{ '#{encoded}' | relative_url }}"
  marker
end

def local_target(value, book)
  return value if value.match?(%r{\A(?:[a-z][a-z0-9+.-]*:|//)}i)
  return "#reader-#{book['key']}" if value == '#'
  return "#reader-#{book['key']}--#{value[1..]}" if value.start_with?('#')

  url = Addressable::URI.parse(value)
  path = Addressable::URI.unencode_component(url.path.to_s)
  target = if path.start_with?('/')
             Pathname.new(path).cleanpath.to_s
           else
             source_dir = Pathname.new("/#{BOOK_ROOT}/#{book['file']}").dirname
             source_dir.join(path).cleanpath.to_s
           end
  raise "Local resource escapes project: #{value}" unless target.start_with?("/#{BOOK_ROOT}/")

  if target.end_with?('/README.md')
    target = target.delete_suffix('README.md')
  elsif target.end_with?('.md')
    target = target.delete_suffix('.md') + '.html'
  end
  result = project_url(target)
  result += "?#{url.query}" if url.query
  result += "##{url.fragment}" if url.fragment
  result
end

def render_book(book)
  source_path = ROOT.join(BOOK_ROOT, book['file'])
  source = source_path.read(encoding: 'UTF-8')
  # The standalone export marker is not a reading-page paragraph.
  source = source.gsub(/^\[TOC\]\s*$/, '')
  converted = Kramdown::Document.new(
    source, input: 'GFM', math_engine: 'mathjax', syntax_highlighter: 'rouge'
  ).to_html
  fragment = Nokogiri::HTML.fragment(converted)
  chapters = []
  fragment.css('h2[id]').each do |heading|
    chapters << { 'label' => heading.text, 'id' => "reader-#{book['key']}--#{heading['id']}" }
  end
  fragment.css('[id]').each { |node| node['id'] = "reader-#{book['key']}--#{node['id']}" }
  fragment.css('[href], [src]').each do |node|
    %w[href src].each do |attribute|
      node[attribute] = local_target(node[attribute], book) if node[attribute]
    end
  end
  # Keep one page-level h1; book titles and chapters live below it.
  fragment.css('h1, h2, h3, h4, h5').each do |node|
    node.name = "h#{node.name[1].to_i + 1}"
  end
  fragment.css('img').each do |image|
    image['loading'] = 'lazy'
    image['decoding'] = 'async'
  end
  metadata = book.merge(
    'source_path' => "#{BOOK_ROOT}/#{book['file']}",
    'sha256' => Digest::SHA256.file(source_path).hexdigest,
    'fragment' => "physical-ai/books/#{book['key']}.html",
    'chapters' => chapters
  )
  rendered = fragment.to_html.rstrip
  # Nokogiri percent-encodes spaces in URI attributes. Substitute Liquid only
  # after serialization so Jekyll sees real expressions, not "{{%20...}}".
  PROJECT_URLS.each { |marker, liquid| rendered = rendered.gsub(marker, liquid) }
  [metadata, "<!-- Generated from #{metadata['source_path']}; edit the source, not this fragment. -->\n#{rendered}\n"]
end

def build(check: false)
  metadata = []
  outputs = {}
  BOOKS.each do |book|
    record, html = render_book(book)
    metadata << record
    outputs[ROOT.join('_includes', record['fragment'])] = html
  end
  outputs[ROOT.join('_data/physical_ai_books.yml')] = { 'books' => metadata }.to_yaml
  stale = outputs.keys.select { |path| !path.file? || path.read(encoding: 'UTF-8') != outputs[path] }
  if check
    raise "Reading fragments are stale: #{stale.map { |p| p.relative_path_from(ROOT) }.join(', ')}" unless stale.empty?
  else
    outputs.each do |path, contents|
      path.dirname.mkpath
      path.write(contents, encoding: 'UTF-8')
    end
  end
  puts JSON.pretty_generate(
    books: metadata.length, chapter_anchors: metadata.sum { |book| book['chapters'].length },
    status: check ? 'fresh' : 'generated'
  )
end

build(check: ARGV.include?('--check')) if $PROGRAM_NAME == __FILE__
