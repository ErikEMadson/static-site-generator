import shutil
from pathlib import Path
from typing import Callable


def recursively_act(
    action: Callable[[Path, Path | None], None],
    logger: Callable[[Path, Path | None, Exception | None], None],
    source: Path,
    destination: Path | None,
    action_first: bool,
) -> None:
    if source.exists():
        if action_first:
            if destination is None or destination.parent.exists():
                try:
                    action(source, destination)
                    logger(source, destination, None)
                except Exception as e:
                    logger(source, destination, e)

        if source.is_dir():
            for next_source in source.iterdir():
                next_destination = (
                    destination.joinpath(next_source.name)
                    if destination is not None
                    else None
                )
                recursively_act(
                    action, logger, next_source, next_destination, action_first
                )

        if not action_first:
            if destination is None or destination.parent.exists():
                try:
                    action(source, destination)
                    logger(source, destination, None)
                except Exception as e:
                    logger(source, destination, e)


def delete_action(source: Path, _destination: Path | None) -> None:
    if source.is_file():
        source.unlink()
    else:
        source.rmdir()


def copy_action(source: Path, destination: Path | None) -> None:
    if destination is None:
        raise ValueError("Cannot copy to a destination of None")

    if source.is_file():
        _ = shutil.copy(source, destination)
    else:
        destination.mkdir(exist_ok=True)


def delete_logger(
    source: Path, _destination: Path | None, exception: Exception | None
) -> None:
    if exception is None:
        print(f"Deleting {source}")
    if exception is not None:
        print(f"Attempted to delete {source} but encountered an exception")
        print(exception.__traceback__)


def copy_logger(
    source: Path, destination: Path | None, exception: Exception | None
) -> None:
    if exception is None:
        print(f"Copying from {source} to {destination}")
    if exception is not None:
        print(
            f"Attempted to copy from {source} to {destination} but encountered an exception"
        )
        print(exception.__traceback__)


def static_to_clean_public() -> None:
    source = Path("static").absolute()
    destination = Path("public").absolute()
    recursively_act(delete_action, delete_logger, destination, None, False)
    recursively_act(copy_action, copy_logger, source, destination, True)


def extract_title(markdown: str) -> str:
    pass


def main() -> None:
    print("Begining main")
    static_to_clean_public()
    print("Finishing main")


if __name__ == "__main__":
    main()
