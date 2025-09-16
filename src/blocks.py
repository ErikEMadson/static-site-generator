import re
from collections.abc import Generator, Sequence
from enum import Enum, auto


class BlockType(Enum):
    HEADING = auto()
    CODE = auto()
    QUOTE = auto()
    UNORDERED_LIST = auto()
    ORDERED_LIST = auto()
    PARAGRAPH = auto()


def list_regex(item_start: str, alternate_start: str | None = None) -> str:
    if alternate_start is None:
        return (
            rf"(?:^|(?:\r?\n))[^\S\r\n]*(?:"
            rf"(?:[^\S\r\n]*{item_start}(?:[^\S\r\n].*)?\r?\n)*)"
            rf"[^\S\r\n]*{item_start}[^\S\r\n].*"
        )
    return (
        rf"(?:^|(?:\r?\n))(?:"
        rf"(?:[^\S\r\n]*(?:"
        rf"(?:[^\S\r\n]*{item_start}(?:[^\S\r\n].*)?\r?\n)*)"
        rf"[^\S\r\n]*{item_start}[^\S\r\n].*)"
        rf"|(?:"
        rf"[^\S\r\n]*(?:"
        rf"(?:[^\S\r\n]*{alternate_start}(?:[^\S\r\n].*)?\r?\n)*)"
        rf"[^\S\r\n]*{alternate_start}[^\S\r\n].*))"
    )


def code_block_iterator(
    text: str,
    block_type: BlockType = BlockType.PARAGRAPH,
    props: dict[str, str] | None = None,
) -> Generator[tuple[str, BlockType, dict[str, str]]]:
    if props is None:
        props = {}
    block_start = 0
    language: str | None = None
    for block in re.finditer(
        r"(?:^|(?:\r?\n))[^\S\r\n]*```([^\S\r\n]*(?P<language>.*?))?[^\S\r\n]*(?:$|(?:\r?\n))",
        text,
    ):
        if block_type is BlockType.CODE and block.group("language"):
            continue
        next_block_start = (
            block.end() if block_type is BlockType.CODE else block.start()
        )
        if block.start() > block_start:
            yield_props = props.copy()
            if language is not None and language != "":
                if "class" in yield_props:
                    yield_props["class"] += f" language-{language}"
                else:
                    yield_props["class"] = f"language-{language}"
            yield (
                text[block_start:next_block_start],
                block_type,
                yield_props,
            )
        block_start = next_block_start
        block_type = (
            BlockType.PARAGRAPH
            if block_type is BlockType.CODE
            else BlockType.CODE
        )
        language = block.group("language")
    yield text[block_start:], block_type, props.copy()


def header_block_iterator(
    text: str,
    block_type: BlockType = BlockType.PARAGRAPH,
    props: dict[str, str] | None = None,
) -> Generator[tuple[str, BlockType, dict[str, str]]]:
    if props is None:
        props = {}
    if block_type is not BlockType.PARAGRAPH:
        yield text, block_type, props.copy()
        return
    block_start = 0
    for block in re.finditer(
        r"(?:^|(?:\r?\n))[^\S\r\n]*(?P<hashcount>#{1,6})[^\S\r\n]+(?P<header>.*?)[^\S\r\n]*(?:$|(?:\r?\n))",
        text,
    ):
        if block.start() > block_start:
            yield (
                text[block_start : block.start()],
                block_type,
                props.copy(),
            )
        yield_props = props.copy()
        yield_props["heading"] = str(len(block.group("hashcount")))
        yield (
            text[block.start() : block.end()],
            BlockType.HEADING,
            yield_props,
        )
        block_start = block.end()
    yield text[block_start:], block_type, props.copy()


def quote_block_iterator(
    text: str,
    block_type: BlockType = BlockType.PARAGRAPH,
    props: dict[str, str] | None = None,
) -> Generator[tuple[str, BlockType, dict[str, str]]]:
    if props is None:
        props = {}
    if block_type is not BlockType.PARAGRAPH:
        yield text, block_type, props.copy()
        return
    block_start = 0
    for block in re.finditer(list_regex(r">"), text):
        if block.start() > block_start:
            yield (
                text[block_start : block.start()],
                block_type,
                props.copy(),
            )
        yield (
            text[block.start() : block.end()],
            BlockType.QUOTE,
            props.copy(),
        )
        block_start = block.end()
    yield text[block_start:], block_type, props.copy()


def ordered_list_block_iterator(
    text: str,
    block_type: BlockType = BlockType.PARAGRAPH,
    props: dict[str, str] | None = None,
) -> Generator[tuple[str, BlockType, dict[str, str]]]:
    if props is None:
        props = {}
    if block_type is not BlockType.PARAGRAPH:
        yield text, block_type, props.copy()
        return
    block_start = 0
    for block in re.finditer(list_regex(r"\d+\."), text):
        if block.start() > block_start:
            yield (
                text[block_start : block.start()],
                block_type,
                props.copy(),
            )
        yield (
            text[block.start() : block.end()],
            BlockType.ORDERED_LIST,
            props.copy(),
        )
        block_start = block.end()
    yield text[block_start:], block_type, props.copy()


def unordered_list_block_iterator(
    text: str,
    block_type: BlockType = BlockType.PARAGRAPH,
    props: dict[str, str] | None = None,
) -> Generator[tuple[str, BlockType, dict[str, str]]]:
    if props is None:
        props = {}
    if block_type is not BlockType.PARAGRAPH:
        yield text, block_type, props.copy()
        return
    block_start = 0
    for block in re.finditer(list_regex(r"\*", r"\-"), text):
        if block.start() > block_start:
            yield (
                text[block_start : block.start()],
                block_type,
                props.copy(),
            )
        yield (
            text[block.start() : block.end()],
            BlockType.UNORDERED_LIST,
            props.copy(),
        )
        block_start = block.end()
    yield text[block_start:], block_type, props.copy()


def paragraph_block_iterator(
    text: str,
    block_type: BlockType = BlockType.PARAGRAPH,
    props: dict[str, str] | None = None,
) -> Generator[tuple[str, BlockType, dict[str, str]]]:
    if props is None:
        props = {}
    if block_type is not BlockType.PARAGRAPH:
        yield text, block_type, props.copy()
        return
    block_start = 0
    for block in re.finditer(r"(?:\r?\n)+", text):
        newlines = block.group().count("\n")
        if block.start() > block_start and newlines > 1:
            yield (
                text[block_start : block.start()],
                block_type,
                props.copy(),
            )
            block_start = block.end()
    yield text[block_start:], block_type, props.copy()


def split_blocks(
    text: str,
) -> Sequence[tuple[str, BlockType, dict[str, str]]]:
    return [
        (
            (
                p[0].strip()
                if p[1] is not BlockType.PARAGRAPH
                else p[0].strip().replace("\n", " ")
            ),
            p[1],
            p[2],
        )
        for c in code_block_iterator(text)
        for h in header_block_iterator(*c)
        for q in quote_block_iterator(*h)
        for ol in ordered_list_block_iterator(*q)
        for ul in unordered_list_block_iterator(*ol)
        for p in paragraph_block_iterator(*ul)
        if p[0].strip() != ""
    ]


def extract_title(text: str) -> str | None:
    for c in code_block_iterator(text):
        for h in header_block_iterator(*c):
            if h[1] == BlockType.HEADING and h[2] and h[2].get("heading"):
                if h[2]["heading"] == "1":
                    return h[0].strip()[2:]
    return None
