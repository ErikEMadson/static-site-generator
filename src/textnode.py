from __future__ import annotations

import re
from collections.abc import Sequence
from enum import Enum, auto
from typing import override

from leafnode import LeafNode


class TextType(Enum):
    PLAIN = auto()
    BOLD = auto()
    ITALIC = auto()
    CODE = auto()
    LINK = auto()
    IMAGE = auto()


class TextNode:
    def __init__(
        self, text: str, text_type: TextType, url: str | None = None
    ) -> None:
        self.text: str = text
        self.text_type: TextType = text_type
        self.url: str | None = url

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, TextNode):
            return (
                self.text == other.text
                and self.text_type == other.text_type
                and self.url == other.url
            )
        return NotImplemented

    @override
    def __repr__(self) -> str:
        if self.url is None:
            return f'TextNode("{self.text.encode("unicode_escape").decode("utf-8")}", {self.text_type}, None)'
        else:
            return f'TextNode("{self.text.encode("unicode_escape").decode("utf-8")}", {self.text_type}, "{self.url.encode("unicode_escape").decode("utf-8")}")'

    def to_html_node(self, props: dict[str, str] | None = None) -> LeafNode:
        match self.text_type:
            case TextType.PLAIN:
                return LeafNode(None, self.text, props)
            case TextType.BOLD:
                return LeafNode("b", self.text, props)
            case TextType.ITALIC:
                return LeafNode("i", self.text, props)
            case TextType.CODE:
                return LeafNode("code", self.text, props)
            case TextType.LINK:
                if self.url is not None:
                    if props is None:
                        props = {}
                    else:
                        props = props.copy()
                    props["href"] = self.url
                    return LeafNode("a", self.text, props)
                else:
                    raise ValueError(
                        "Expected LINK type TextNode to have a non-null URL"
                    )
            case TextType.IMAGE:
                if self.url is not None:
                    if props is None:
                        props = {}
                    else:
                        props = props.copy()
                    props["src"] = self.url
                    props["alt"] = self.text
                    return LeafNode("img", None, props)
                else:
                    raise ValueError(
                        "Expected IMAGE type TextNode to have a non-null URL"
                    )

    def _split_nodes_delimiter(self, delimiter: str) -> Sequence[TextNode]:
        if self.text_type is not TextType.PLAIN:
            return [self]
        splits = self.text.split(delimiter)
        if len(splits) % 2 != 1:
            raise ValueError(
                f"There is a mismatch in the occurances of delimiter {delimiter} in the text"
            )
        match delimiter:
            case "`":
                next_type = TextType.CODE
            case "**":
                next_type = TextType.BOLD
            case "_":
                next_type = TextType.ITALIC
            case _:
                raise NotImplementedError(
                    f"Delimiter {delimiter} not recognized"
                )
        current_type = TextType.PLAIN
        text_nodes: list[TextNode] = []
        for split in splits:
            text_nodes.append(TextNode(split, current_type))
            current_type, next_type = next_type, current_type
        return text_nodes

    def _split_images_and_links(self) -> Sequence[TextNode]:
        if self.text_type is not TextType.PLAIN:
            return [self]
        result_list: list[TextNode] = []
        next_start = 0
        for image in re.finditer(
            r"(?P<type>!)?\[(?P<alt>.*?)]\((?P<url>.*?)\)", self.text
        ):
            if image.start() > next_start:
                result_list.append(
                    TextNode(
                        self.text[next_start : image.start()], TextType.PLAIN
                    )
                )
            if image.group("type") is None:
                result_list.append(
                    TextNode(
                        image.group("alt"), TextType.LINK, image.group("url")
                    )
                )
            else:
                result_list.append(
                    TextNode(
                        image.group("alt"), TextType.IMAGE, image.group("url")
                    )
                )
            next_start = image.end() + 1
        result_list.append(TextNode(self.text[next_start:], TextType.PLAIN))
        return result_list

    def split_node(self) -> Sequence[TextNode]:
        return [
            bold_node
            for code_node in self._split_nodes_delimiter("`")
            for image_node in code_node._split_images_and_links()
            for italic_node in image_node._split_nodes_delimiter("_")
            for bold_node in italic_node._split_nodes_delimiter("**")
            if bold_node.text != "" or bold_node.text_type is not TextType.PLAIN
        ]

    @staticmethod
    def split_text(text: str) -> Sequence[TextNode]:
        return TextNode(text, TextType.PLAIN).split_node()
