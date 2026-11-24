"""Milestone 4 document iteration."""

import pytest

from bs4 import BeautifulSoup
from bs4.element import Comment, Doctype, NavigableString


def test_nested_tags_and_text_are_yielded_in_document_order():
    soup = BeautifulSoup("<div><b>one</b><i>two</i></div><p>three</p>", "html.parser")

    nodes = iter(soup)
    assert next(nodes) is soup.div
    assert next(nodes) is soup.b
    assert next(iter(soup)) is soup.div
    assert next(nodes) is soup.b.string
    assert next(nodes) is soup.i
    assert next(nodes) is soup.i.string
    assert next(nodes) is soup.p
    assert next(nodes) is soup.p.string
    with pytest.raises(StopIteration):
        next(nodes)

    assert list(soup.div) == [soup.b, soup.i]


def test_plain_text_is_yielded_as_a_navigable_string():
    soup = BeautifulSoup("Just text", "html.parser")

    node, = soup

    assert type(node) is NavigableString
    assert node == "Just text"
    assert node is soup.string


def test_comments_are_yielded_at_top_level_and_inside_tags():
    soup = BeautifulSoup("<!--top--><p><!--nested-->text</p>", "html.parser")

    top, paragraph, nested, body = soup

    assert isinstance(top, Comment)
    assert top == "top"
    assert paragraph is soup.p
    assert isinstance(nested, Comment)
    assert nested == "nested"
    assert body == "text"


def test_doctype_is_yielded_before_the_document_element():
    soup = BeautifulSoup("<!DOCTYPE html><html><head></head></html>", "html.parser")

    doctype, html, head = soup

    assert isinstance(doctype, Doctype)
    assert doctype == "html"
    assert html is soup.html
    assert head is soup.head


def test_empty_document_yields_no_nodes():
    soup = BeautifulSoup("", "html.parser")

    with pytest.raises(StopIteration):
        next(iter(soup))
