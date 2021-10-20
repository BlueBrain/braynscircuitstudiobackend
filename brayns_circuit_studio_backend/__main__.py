"""Application main module."""
from api_version import VersionEntryPoint
from backend import Server
from version import __version__


def main():
    """Application's main function.

    Display the version and start the WebSocket server.
    """
    print_box(f"Brayns Circuit Studio Backend v{__version__}")
    Server([VersionEntryPoint(__version__)])


def print_box(line: str) -> None:
    """Surround `line` by a box."""
    print(f"+-{'-' * len(line)}-+")
    print(f"| {line} |")
    print(f"+-{'-' * len(line)}-+")


if __name__ == "__main__":
    main()
