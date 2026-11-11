"""Milestone 3 transformer callbacks and Task 7."""

from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from bs4 import BeautifulSoup, SoupReplacer
from bs4.builder._htmlparser import HTMLParserTreeBuilder
from bs4.element import Tag


def test_name_transformer_preserves_nesting_and_uses_attributes():
    def rename(tag):
        return "strong" if tag.name == "b" and tag.has_attr("id") else tag.name

    soup = BeautifulSoup(
        '<b id="outer"><b>inside</b></b><x:p>after</x:p>',
        "html.parser",
        replacer=SoupReplacer(name_xformer=rename),
    )
    assert str(soup) == '<strong id="outer"><b>inside</b></strong><x:p>after</x:p>'


def test_attribute_transformer_replaces_entire_mapping():
    def replace_attrs(tag):
        return {"id": tag["id"]} if tag.name == "p" else {}

    soup = BeautifulSoup(
        '<p id="keep" class="old"><b title="remove">text</b></p>',
        "html.parser",
        replacer=SoupReplacer(attrs_xformer=replace_attrs),
    )
    assert str(soup) == '<p id="keep"><b>text</b></p>'


def test_in_place_transformer_updates_contents_and_keeps_following_nodes_linked():
    def rewrite(tag):
        if tag.name == "p":
            del tag["class"]
            tag.string = "new"

    soup = BeautifulSoup(
        '<p class="old"><b>old</b></p><span>after</span>',
        "html.parser",
        replacer=SoupReplacer(xformer=rewrite),
    )
    assert str(soup) == "<p>new</p><span>after</span>"
    assert soup.p.string.next_element is soup.span
    assert soup.span.previous_element is soup.p.string


def test_transformers_run_in_name_attributes_in_place_order():
    def finish(tag):
        tag["title"] = tag["id"]

    replacer = SoupReplacer(
        name_xformer=lambda tag: "strong",
        attrs_xformer=lambda tag: {"id": tag.name},
        xformer=finish,
    )
    soup = BeautifulSoup("<b>text</b>", "html.parser", replacer=replacer)
    assert str(soup) == '<strong id="strong" title="strong">text</strong>'


def test_transformer_runs_inside_builder_feed_without_a_tree_search():
    class ObservingBuilder(HTMLParserTreeBuilder):
        def feed(self, markup):
            super().feed(markup)
            assert self.soup.contents[0].attrs == {"id": "during-parse"}

    replacer = SoupReplacer(attrs_xformer=lambda tag: {"id": "during-parse"})
    with patch.object(Tag, "find_all", side_effect=AssertionError("extra tree search")):
        BeautifulSoup("<p>text</p>", builder=ObservingBuilder(), replacer=replacer)


def test_task7_adds_and_replaces_paragraph_classes(tmp_path):
    script = Path(__file__).resolve().parents[2] / "apps" / "m3" / "task7.py"
    source = tmp_path / "input.html"
    output = tmp_path / "output.html"
    markup = '<p id="keep" class="old other">one</p><p>two</p><div class="old">three</div>'
    source.write_text(markup, encoding="utf-8")

    subprocess.run([sys.executable, script, source, "-o", output], cwd=tmp_path, check=True)

    assert source.read_text(encoding="utf-8") == markup
    assert output.read_text(encoding="utf-8") == (
        '<p class="test" id="keep">one</p><p class="test">two</p><div class="old">three</div>'
    )
