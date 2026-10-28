"""Milestone 2: parse-time replacement, tree integrity, and compatibility."""

import copy
import pickle
from unittest.mock import patch

import pytest

from bs4 import BeautifulSoup, SoupReplacer, SoupStrainer
from bs4.builder._htmlparser import HTMLParserTreeBuilder
from bs4.element import Tag
from bs4.tests import HTML5LIB_PRESENT, LXML_PRESENT


PARSERS = [
    "html.parser",
    pytest.param("lxml", marks=pytest.mark.skipif(not LXML_PRESENT, reason="lxml")),
    pytest.param("xml", marks=pytest.mark.skipif(not LXML_PRESENT, reason="lxml")),
]


@pytest.mark.parametrize("parser", PARSERS)
def test_replaces_all_b_tags(parser):
    """Required case 1: every match changes; attributes and children survive."""
    soup = BeautifulSoup(
        '<root><b id="one" class="bold">A<i>B</i></b><b>C</b><p>D</p></root>',
        parser,
        replacer=SoupReplacer("b", "blockquote"),
    )
    assert soup.find_all("b") == []
    tags = soup.find_all("blockquote")
    assert len(tags) == 2
    assert tags[0]["id"] == "one"
    assert tags[0].get_text() == "AB"
    assert tags[0].i.parent is tags[0]
    assert soup.p.string == "D"
    assert tags[0]["class"] == ("bold" if parser == "xml" else ["bold"])


@pytest.mark.parametrize("parser", PARSERS)
def test_nested_replacements_keep_closing_tags_and_siblings(parser):
    """Required case 2: original </b> events still close the right nodes."""
    markup = '<root><b id="outer">A<b id="inner">B</b>C</b><p>D</p></root>'
    expected = BeautifulSoup(markup, parser)
    for tag in expected.find_all("b"):
        tag.name = "blockquote"
    actual = BeautifulSoup(markup, parser, replacer=SoupReplacer("b", "blockquote"))
    assert actual == expected
    assert actual.p.parent is actual.root
    assert actual.find(id="inner").parent is actual.find(id="outer")


@pytest.mark.parametrize("parser", PARSERS)
@pytest.mark.parametrize(
    "markup,original,alternative",
    [
        ("<root><b>X</b></root>", "missing", "blockquote"),
        ("<root><b>X</b></root>", "b", "b"),
        ("<root><b/><p>X</p></root>", "b", "blockquote"),
        ("<root><br/><p>X</p></root>", "br", "separator"),
        ("<root><b>X</b></root>", "b", "br"),
        ("<root><pre>  X\n Y  </pre><p>Z</p></root>", "pre", "section"),
        ('<root><script>if (a &lt; b) x()</script><p>Z</p></root>', "script", "code"),
        ("<root><B>X</B><b>Y</b></root>", "B", "strong"),
        ("<root/>", "root", "document"),
        ("", "b", "blockquote"),
    ],
)
def test_matches_existing_post_parse_rename(parser, markup, original, alternative):
    expected = BeautifulSoup(markup, parser)
    for tag in expected.find_all(original):
        tag.name = alternative
    actual = BeautifulSoup(markup, parser, replacer=SoupReplacer(original, alternative))
    assert actual == expected
    assert str(actual) == str(expected)


@pytest.mark.parametrize("markup", ["<b>unclosed", "<div><b>A<i>B</div><p>C</p>"])
def test_implicit_and_end_of_file_closes(markup):
    expected = BeautifulSoup(markup, "html.parser")
    for tag in expected.find_all("b"):
        tag.name = "blockquote"
    assert BeautifulSoup(markup, "html.parser", replacer=SoupReplacer("b", "blockquote")) == expected


@pytest.mark.parametrize("parser", PARSERS)
def test_strainer_uses_original_names(parser):
    soup = BeautifulSoup(
        '<root><b>A<i>B</i></b><p>excluded</p><b>C</b></root>',
        parser,
        parse_only=SoupStrainer("b"),
        replacer=SoupReplacer("b", "blockquote"),
    )
    assert [tag.name for tag in soup.find_all(True)] == ["blockquote", "i", "blockquote"]
    assert soup.get_text() == "ABC"


def test_replacement_happens_inside_builder_feed_without_search():
    class ObservingBuilder(HTMLParserTreeBuilder):
        def feed(self, markup):
            # Constructor has not returned and _feed's final cleanup has
            # not run. The closed node must already have its new name.
            super().feed(markup)
            assert self.soup.contents[0].name == "blockquote"

    with patch.object(Tag, "find_all", side_effect=AssertionError("extra tree search")):
        soup = BeautifulSoup("<b>X</b><p>Y</p>", builder=ObservingBuilder(),
                             replacer=SoupReplacer("b", "blockquote"))
    assert str(soup) == "<blockquote>X</blockquote><p>Y</p>"


def test_replacer_reuse_and_omitted_argument():
    replacer = SoupReplacer("b", "blockquote")
    for _ in range(2):
        assert str(BeautifulSoup("<b>X</b>", "html.parser", replacer=replacer)) == "<blockquote>X</blockquote>"
    assert str(BeautifulSoup("<b>X</b>", "html.parser")) == "<b>X</b>"


@pytest.mark.skipif(not LXML_PRESENT, reason="lxml")
def test_xml_namespace_and_case_are_preserved():
    soup = BeautifulSoup('<r xmlns:x="urn:test"><x:b id="q">X</x:b><B>Y</B></r>',
                         "xml", replacer=SoupReplacer("b", "blockquote"))
    tag = soup.find("blockquote")
    assert (tag.prefix, tag.namespace, tag["id"]) == ("x", "urn:test", "q")
    assert soup.B.string == "Y"
    assert '<x:blockquote id="q">X</x:blockquote>' in str(soup)


def test_copy_and_pickle_preserve_tree():
    soup = BeautifulSoup("<b>X</b><p>Y</p>", "html.parser", replacer=SoupReplacer("b", "blockquote"))
    assert copy.deepcopy(soup) == soup
    assert pickle.loads(pickle.dumps(soup)) == soup


@pytest.mark.parametrize("name", [None, 5, [], object()])
def test_constructor_rejects_non_string_names(name):
    with pytest.raises(TypeError):
        SoupReplacer(name, "b")
    with pytest.raises(TypeError):
        SoupReplacer("b", name)


@pytest.mark.parametrize("name", ["", "<b>", "b b", "b/", "x:b", "[document]", "b\x00"])
def test_constructor_rejects_invalid_names(name):
    with pytest.raises(ValueError):
        SoupReplacer(name, "b")
    with pytest.raises(ValueError):
        SoupReplacer("b", name)


def test_invalid_replacer_argument():
    with pytest.raises(TypeError, match="SoupReplacer"):
        BeautifulSoup("<b>X</b>", "html.parser", replacer=("b", "blockquote"))


@pytest.mark.skipif(not HTML5LIB_PRESENT, reason="html5lib")
def test_html5lib_fails_explicitly_instead_of_silently_ignoring_replacer():
    with pytest.raises(ValueError, match="html5lib"):
        BeautifulSoup("<b>X</b>", "html5lib", replacer=SoupReplacer("b", "blockquote"))
