from __future__ import annotations

from collections.abc import Sequence
from typing import override


class HTMLNode:
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: Sequence[HTMLNode] | None = None,
        props: dict[str, str] | None = None,
    ) -> None:
        self.tag: str | None = tag
        self.value: str | None = value
        self.children: Sequence[HTMLNode] = (
            children if children is not None else []
        )
        self.props: dict[str, str] | None = props if props is not None else {}

    def to_html(self) -> str:
        raise NotImplementedError()

    def props_to_html(self) -> str:
        if self.props is None:
            return ""
        return_string = ""
        for k, v in self.props.items():
            return_string += f' {k}="{v}"'
        return return_string

    @override
    def __repr__(self) -> str:
        return f"HTMLNode({repr(self.tag)}, {repr(self.value)}, {repr(self.children)}, {repr(self.props)})"
