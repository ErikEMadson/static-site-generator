import re
import shutil
import sys
from pathlib import Path
from typing import Callable

import blocks
from parentnode import ParentNode


def recursively_act(
    action: Callable[[Path, Path | None, tuple[object, ...] | None], None],
    logger: Callable[
        [Path, Path | None, Exception | None, tuple[object, ...] | None], None
    ],
    source: Path,
    destination: Path | None,
    action_first: bool,
    payload: tuple[object, ...] | None = None,
) -> None:
    if source.exists():
        if action_first:
            if destination is None or destination.parent.exists():
                try:
                    action(source, destination, payload)
                    logger(source, destination, None, payload)
                except Exception as e:
                    logger(source, destination, e, payload)

        if source.is_dir():
            for next_source in source.iterdir():
                next_destination = (
                    destination.joinpath(next_source.name)
                    if destination is not None
                    else None
                )
                recursively_act(
                    action,
                    logger,
                    next_source,
                    next_destination,
                    action_first,
                    payload,
                )

        if not action_first:
            if destination is None or destination.parent.exists():
                try:
                    action(source, destination, payload)
                    logger(source, destination, None, payload)
                except Exception as e:
                    logger(source, destination, e, payload)


def delete_action(
    source: Path, _destination: Path | None, _payload: tuple[object, ...] | None
) -> None:
    if source.is_file():
        source.unlink()
    else:
        source.rmdir()


def copy_action(
    source: Path, destination: Path | None, _payload: tuple[object, ...] | None
) -> None:
    if destination is None:
        raise ValueError("Cannot copy to a destination of None")

    if source.is_file():
        _ = shutil.copy(source, destination)
    else:
        destination.mkdir()


def delete_logger(
    source: Path,
    _destination: Path | None,
    exception: Exception | None,
    _payload: tuple[object, ...] | None,
) -> None:
    if exception is None:
        print(f"Deleting {source}")
    else:
        print(f"Attempted to delete {source} but encountered an exception")
        print(exception.__traceback__)


def copy_logger(
    source: Path,
    destination: Path | None,
    exception: Exception | None,
    _payload: tuple[object, ...] | None,
) -> None:
    if exception is None:
        print(f"Copying from {source} to {destination}")
    else:
        print(
            f"Attempted to copy from {source} to {destination} but encountered an exception"
        )
        print(exception.__traceback__)


def generate_page_action(
    source: Path, destination: Path | None, payload: tuple[object, ...] | None
) -> None:
    if destination is None:
        raise ValueError("Cannot copy to a destination of None")
    if payload is None or len(payload) == 0:
        payload = ("",)

    if source.is_dir():
        destination.mkdir(exist_ok=True)
    else:
        with open(source, "r", encoding="utf-8") as file:
            markdown = file.read()
        with open("template.html", "r", encoding="utf-8") as file:
            template = file.read()
        content = ParentNode.from_markdown(markdown).to_html()
        title = blocks.extract_title(markdown)
        if title is None:
            raise ValueError(
                "Markdown is required to have an h1 heading (single #) as a title."
            )
        html = template.replace("{{ Title }}", title).replace(
            "{{ Content }}", content
        )
        string_builder: list[str] = []
        next_start = 0
        for link in re.finditer(
            r"(?P<type>(?:href)|(?:src))[^\S\r\n]*=[^\S\r\n]*\"(?P<link>[^\"]*)\"",
            html,
        ):
            string_builder.append(html[next_start : link.start()])
            try:
                new_path = Path("/").joinpath(
                    Path(str(payload[0])).joinpath(
                        Path(link.group("link")).relative_to("/")
                    )
                )
                string_builder.append(f'{link.group("type")}="{new_path}"')
            except Exception:
                string_builder.append(html[link.start() : link.end()])
            next_start = link.end()
        string_builder.append(html[next_start:])
        html = "".join(string_builder)
        destination = destination.with_suffix(".html")
        with open(destination, "w", encoding="utf-8") as file:
            _ = file.write(html)


def generate_page_logger(
    source: Path,
    destination: Path | None,
    exception: Exception | None,
    _payload: tuple[object, ...] | None,
) -> None:
    if source.is_dir():
        if exception is None:
            print(f"Creating directory mirroring {source} at {destination}")
        else:
            print(
                f"Attempted to create directory mirroring {source} at {destination} using template.html but encountered an exception"
            )
            print(exception.__traceback__)
    else:
        if destination is not None:
            destination = destination.with_suffix(".html")
        if exception is None:
            print(
                f"Generated page from {source} to {destination} using template.html"
            )
        else:
            print(
                f"Attempted to generate page from {source} to {destination} using template.html but encountered an exception"
            )
            print(exception.__traceback__)


def content_generation(path_prefix: str | None, destination: str) -> None:
    static_dir = Path("static").absolute()
    public_dir = Path(destination).absolute()
    content_dir = Path("content").absolute()
    recursively_act(delete_action, delete_logger, public_dir, None, False)
    recursively_act(copy_action, copy_logger, static_dir, public_dir, True)
    recursively_act(
        generate_page_action,
        generate_page_logger,
        content_dir,
        public_dir,
        True,
        (path_prefix,),
    )


def main() -> None:
    if len(sys.argv) > 2:
        destination = sys.argv[2]
    else:
        destination = "public"
    if len(sys.argv) > 1:
        path_prefix = sys.argv[1]
    else:
        path_prefix = None
    print("Begining main")
    content_generation(path_prefix, destination)
    print("Finishing main")


if __name__ == "__main__":
    main()
