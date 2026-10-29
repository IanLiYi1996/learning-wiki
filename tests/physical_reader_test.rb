# frozen_string_literal: true

require 'minitest/autorun'
require_relative '../scripts/build_physical_reader'

class PhysicalReaderRenderingTest < Minitest::Test
  def setup
    @book = BOOKS.find { |book| book['key'] == 'industry' }
  end

  def resolve_marker(target)
    PROJECT_URLS.reduce(target) { |result, (marker, value)| result.gsub(marker, value) }
  end

  def test_relative_images_resolve_from_original_book_directory
    assert_equal "{{ '/wiki/topics/physical-ai/images/industry-lifecycle.png' | relative_url }}",
                 resolve_marker(local_target('../images/industry-lifecycle.png', @book))
  end

  def test_source_markdown_links_become_in_site_pages
    assert_equal "{{ '/wiki/topics/physical-ai/industry/chapters/01_lifecycle.html' | relative_url }}#chapter",
                 resolve_marker(local_target('chapters/01_lifecycle.md#chapter', @book))
  end

  def test_readme_links_keep_directory_routes
    assert_equal "{{ '/wiki/topics/physical-ai/advanced/' | relative_url }}",
                 resolve_marker(local_target('../advanced/README.md', @book))
  end

  def test_anchors_are_namespaced_to_the_book
    assert_equal '#reader-industry--same-title', local_target('#same-title', @book)
    assert_equal '#reader-industry', local_target('#', @book)
  end

  def test_external_primary_sources_remain_unchanged
    url = 'https://example.com/research?q=paper#figure'
    assert_equal url, local_target(url, @book)
  end

  def test_local_path_escape_is_rejected
    assert_raises(RuntimeError) { local_target('../../../../secret.txt', @book) }
  end

  def test_complete_book_has_namespaced_ids_and_real_liquid_urls
    metadata, rendered = render_book(@book)
    assert_includes rendered, '12 把产品接起来：交付接口与原理对照'
    assert_includes rendered, "{{ '/wiki/topics/physical-ai/images/industry-lifecycle.png' | relative_url }}"
    refute_includes rendered, '{{%20'
    refute_includes rendered, '[TOC]'
    document = Nokogiri::HTML.fragment(rendered)
    assert document.css('[id]').all? { |node| node['id'].start_with?('reader-industry--') }
    assert_equal 15, metadata['chapters'].length
  end
end
