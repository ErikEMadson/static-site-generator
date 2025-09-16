from __future__ import annotations

import re
from collections.abc import Sequence
from typing import override

import blocks
from blocks import BlockType
from htmlnode import HTMLNode
from textnode import TextNode, TextType


class ParentNode(HTMLNode):
    def __init__(
        self,
        tag: str | None,
        children: Sequence[HTMLNode] | None,
        props: dict[str, str] | None = None,
    ) -> None:
        super().__init__(tag, None, children, props)

    @override
    def to_html(self) -> str:
        if self.tag is None:
            raise ValueError("Parent node must have a tag")
        if len(self.children) == 0:
            raise ValueError("Parent node must have at least one child")
        return f"<{self.tag}{self.props_to_html()}>{''.join(child.to_html() for child in self.children)}</{self.tag}>"

    @override
    def __repr__(self) -> str:
        return f"ParentNode({repr(self.tag)}, {repr(self.children)}, {repr(self.props)})"

    @staticmethod
    def from_markdown(
        text: str, props: dict[str, str] | None = None
    ) -> HTMLNode:
        children: list[HTMLNode] = []
        for block, block_type, block_props in blocks.split_blocks(text):
            match block_type:
                case BlockType.HEADING:
                    heading = int(block_props.pop("heading"))
                    children.append(
                        ParentNode(
                            f"h{heading}",
                            [
                                node.to_html_node()
                                for node in TextNode.split_text(
                                    block[heading + 1]
                                )
                            ],
                            block_props,
                        )
                    )
                case BlockType.CODE:
                    code = re.match(
                        r"```.*\r?\n(?P<code>[\s\S]*?)(\r?\n)?```", block
                    )
                    if code is not None:
                        children.append(
                            ParentNode(
                                "pre",
                                [
                                    TextNode(
                                        code.group("code"), TextType.CODE
                                    ).to_html_node(block_props)
                                ],
                            )
                        )
                case BlockType.QUOTE:
                    quote = "\n".join(
                        line.group("quote")
                        for line in re.finditer(
                            r"[\S\r\n]*>[\S\r\n]*(?P<quote>.*)(?:\r?\n)?", block
                        )
                    )
                    children.append(
                        ParentNode(
                            "pre",
                            children=[
                                ParentNode(
                                    "blockquote",
                                    [
                                        node.to_html_node()
                                        for node in TextNode.split_text(quote)
                                    ],
                                    block_props,
                                )
                            ],
                        )
                    )
                case BlockType.UNORDERED_LIST:
                    items = [
                        line.group("item")
                        for line in re.finditer(
                            r"[\S\r\n]*(?:(?:\*)|(?:\-))[\S\r\n]*(?P<item>.*)(?:\r?\n)?",
                            block,
                        )
                        if line.group("item")
                    ]
                    list_items = [
                        ParentNode(
                            "li",
                            [
                                node.to_html_node()
                                for node in TextNode.split_text(line)
                            ],
                        )
                        for line in items
                    ]
                    children.append(ParentNode("ul", list_items, block_props))
                case BlockType.ORDERED_LIST:
                    items = [
                        line.group("item")
                        for line in re.finditer(
                            r"[\S\r\n]*\d+\.[\S\r\n]*(?P<item>.*)(?:\r?\n)?",
                            block,
                        )
                        if line.group("item")
                    ]
                    list_items = [
                        ParentNode(
                            "li",
                            [
                                node.to_html_node()
                                for node in TextNode.split_text(line)
                            ],
                        )
                        for line in items
                    ]
                    children.append(ParentNode("ol", list_items, block_props))
                case BlockType.PARAGRAPH:
                    children.append(
                        ParentNode(
                            "p",
                            [
                                node.to_html_node()
                                for node in TextNode.split_text(block)
                            ],
                            block_props,
                        )
                    )
        return ParentNode("div", children, props)
