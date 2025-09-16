from typing import override

from htmlnode import HTMLNode


class LeafNode(HTMLNode):
    def __init__(
        self,
        tag: str | None,
        value: str | None,
        props: dict[str, str] | None = None,
    ) -> None:
        super().__init__(tag, value, None, props)

    @override
    def to_html(self) -> str:
        if self.tag is None:
            if self.value is None:
                raise ValueError(
                    "Expected LeafNode tag or value to not be None"
                )
            else:
                return self.value
        elif self.value is None:
            return f"<{self.tag}{self.props_to_html()}>"
        else:
            return (
                f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
            )

    @override
    def __repr__(self) -> str:
        return f"LeafNode({repr(self.tag)}, {repr(self.value)}, {repr(self.props)})"
