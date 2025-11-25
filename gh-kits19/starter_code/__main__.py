"""CLI entry point for starter_code.

This module exposes two convenience commands:

- download: pull KiTS19 imaging volumes with progress bars.
- visualize: create segmentation overlays for a specific case.

Run `python -m starter_code --help` for usage details.
"""
import argparse
import sys
from typing import Iterable, List, Optional

from . import get_imaging, visualize


def _parse_case_args(case_args: Optional[Iterable[str]]) -> Optional[List[str]]:
    if not case_args:
        return None

    cases: List[str] = []
    for arg in case_args:
        parts = [item.strip() for item in arg.split(",") if item.strip()]
        cases.extend(parts)
    return cases or None


def _add_download_parser(subparsers: argparse._SubParsersAction) -> None:
    dl_parser = subparsers.add_parser(
        "download",
        help="Download imaging volumes into the local data directory.",
    )
    dl_parser.add_argument(
        "-c",
        "--case",
        dest="case_ids",
        action="append",
        help="Case identifier to download (repeatable or comma separated).",
    )
    dl_parser.add_argument(
        "--case-count",
        default=get_imaging.CASE_CNT,
        type=int,
        help="Upper bound (exclusive) when scanning for missing cases.",
    )
    dl_parser.add_argument(
        "--chunk-size",
        default=get_imaging.CHUNK_SIZE,
        type=int,
        help="Chunk size in bytes for streamed downloads.",
    )
    dl_parser.add_argument(
        "--retry-delay",
        default=get_imaging.DEFAULT_RETRY_DELAY,
        type=int,
        help="Seconds to wait before retrying a failed request.",
    )
    dl_parser.add_argument(
        "--max-retries",
        default=get_imaging.MAX_RETRIES,
        type=int,
        help="Maximum number of retry attempts per file.",
    )
    dl_parser.add_argument(
        "--force",
        action="store_true",
        help="Redownload cases even if files already exist.",
    )


def _add_visualize_parser(subparsers: argparse._SubParsersAction) -> None:
    viz_parser = subparsers.add_parser(
        "visualize",
        help="Overlay a segmentation on the imaging volume and export PNGs.",
    )
    viz_parser.add_argument(
        "-c",
        "--case-id",
        required=True,
        help="Case identifier (numeric id or case_XXXXX).",
    )
    viz_parser.add_argument(
        "-d",
        "--destination",
        required=True,
        help="Directory where the generated PNG slices will be stored.",
    )
    viz_parser.add_argument(
        "-u",
        "--upper-hu-bound",
        default=visualize.DEFAULT_HU_MAX,
        type=int,
        help="Upper bound at which to clip HU values.",
    )
    viz_parser.add_argument(
        "-l",
        "--lower-hu-bound",
        default=visualize.DEFAULT_HU_MIN,
        type=int,
        help="Lower bound at which to clip HU values.",
    )
    viz_parser.add_argument(
        "-p",
        "--plane",
        default=visualize.DEFAULT_PLANE,
        choices=["axial", "coronal", "sagittal"],
        help="Plane in which to generate slices.",
    )
    viz_parser.add_argument(
        "-a",
        "--alpha",
        default=visualize.DEFAULT_OVERLAY_ALPHA,
        type=float,
        help="Alpha blend for segmentation overlay.",
    )
    viz_parser.add_argument(
        "--less-ram",
        action="store_true",
        help="Process slices sequentially to reduce peak RAM usage.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="starter_code",
        description="Utility helpers for the KiTS19 starter code.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    _add_download_parser(subparsers)
    _add_visualize_parser(subparsers)
    return parser


def run(args: Optional[List[str]] = None) -> None:
    parser = build_parser()
    parsed = parser.parse_args(args=args)

    if parsed.command == "download":
        case_ids = _parse_case_args(parsed.case_ids)
        get_imaging.download_cases(
            case_ids=case_ids,
            case_count=parsed.case_count,
            chunk_size=parsed.chunk_size,
            retry_delay=parsed.retry_delay,
            max_retries=parsed.max_retries,
            force=parsed.force,
        )
    elif parsed.command == "visualize":
        visualize.visualize(
            parsed.case_id,
            parsed.destination,
            hu_min=parsed.lower_hu_bound,
            hu_max=parsed.upper_hu_bound,
            alpha=parsed.alpha,
            plane=parsed.plane,
            less_ram=parsed.less_ram,
        )
    else:
        parser.print_help()


def main() -> None:
    run(sys.argv[1:])


if __name__ == "__main__":
    main()
