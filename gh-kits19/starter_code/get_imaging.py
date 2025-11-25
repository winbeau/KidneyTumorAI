import os
import sys
import time
from pathlib import Path
from shutil import move
from typing import Iterable, List, Optional, Sequence, Union

import numpy as np
import requests
from tqdm import tqdm

CASE_CNT = 50
IMAGING_URL = "https://kits19.sfo2.digitaloceanspaces.com/"
IMAGING_NAME_TMPLT = "master_{:05d}.nii.gz"
CHUNK_SIZE = 1000
DEFAULT_RETRY_DELAY = 30
MAX_RETRIES = 1000


def _data_root() -> Path:
    """Return the dataset directory (starter_code/../data)."""
    return Path(__file__).resolve().parent.parent / "data"


def get_destination(case_index: int) -> Path:
    """Resolve destination path for a case image."""
    destination = _data_root() / f"case_{case_index:05d}" / "imaging.nii.gz"
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination


def _temp_file() -> Path:
    """Return the temporary download path."""
    return Path(__file__).resolve().parent / "temp.tmp"


def _cleanup(bar: tqdm, msg: str) -> None:
    bar.close()
    temp_f = _temp_file()
    if temp_f.exists():
        temp_f.unlink()
    print(msg)
    sys.exit()


def _normalize_case_id(case_id: Union[int, str]) -> int:
    if isinstance(case_id, int):
        return case_id
    if isinstance(case_id, str):
        if case_id.startswith("case_"):
            return int(case_id.split("_")[1])
        return int(case_id)
    raise TypeError(f"Unsupported case id type: {type(case_id)}")


def resolve_cases_to_download(
    case_ids: Optional[Sequence[Union[int, str]]] = None,
    case_count: int = CASE_CNT,
    force: bool = False,
) -> List[int]:
    """
    Determine which case ids need to be downloaded.

    If case_ids is None, scan the default range and pick cases that are missing.
    """
    if case_ids is None:
        candidates = range(case_count)
    else:
        candidates = [_normalize_case_id(cid) for cid in case_ids]

    todo = []
    for cid in candidates:
        destination = get_destination(cid)
        if force or not destination.exists():
            todo.append(cid)
    return sorted(todo)


def download_case(
    case_id: int,
    session: Optional[requests.Session] = None,
    chunk_size: int = CHUNK_SIZE,
    retry_delay: int = DEFAULT_RETRY_DELAY,
    max_retries: int = MAX_RETRIES,
) -> Path:
    """Download a single case image and return the destination path."""
    destination = get_destination(case_id)

    temp_f = _temp_file()
    remote_name = IMAGING_NAME_TMPLT.format(case_id)
    uri = IMAGING_URL + remote_name

    tries = 0
    sess = session or requests.Session()
    while True:
        try:
            tries += 1
            response = sess.get(uri, stream=True)
            response.raise_for_status()
            break
        except Exception as exc:
            print("Failed to establish connection with server:\n")
            print(f"{exc}\n")
            if tries < max_retries:
                print(f"Retrying in {retry_delay}s")
                time.sleep(retry_delay)
            else:
                print("Max retries exceeded")
                raise

    total = int(np.ceil(int(response.headers.get("content-length", 0)) / chunk_size))

    try:
        with temp_f.open("wb") as f:
            bar = tqdm(unit="KB", desc=f"case_{case_id:05d}", total=total)
            for pkg in response.iter_content(chunk_size=chunk_size):
                f.write(pkg)
                bar.update(max(int(len(pkg) / chunk_size), 1))
            bar.close()
        move(str(temp_f), destination)
        return destination
    except KeyboardInterrupt:
        _cleanup(bar, "KeyboardInterrupt")
    except Exception as exc:
        _cleanup(bar, str(exc))
    finally:
        if temp_f.exists():
            temp_f.unlink()
    return destination


def download_cases(
    case_ids: Optional[Sequence[Union[int, str]]] = None,
    case_count: int = CASE_CNT,
    chunk_size: int = CHUNK_SIZE,
    retry_delay: int = DEFAULT_RETRY_DELAY,
    max_retries: int = MAX_RETRIES,
    force: bool = False,
) -> List[Path]:
    """Download one or more cases and return the list of destination paths."""
    todo = resolve_cases_to_download(case_ids, case_count=case_count, force=force)

    print(f"{len(todo)} cases to download...")
    if not todo:
        return []

    destinations: List[Path] = []
    with requests.Session() as session:
        for idx, cid in enumerate(todo, start=1):
            print(f"Download {idx}/{len(todo)}:")
            dest = download_case(
                cid,
                session=session,
                chunk_size=chunk_size,
                retry_delay=retry_delay,
                max_retries=max_retries,
            )
            destinations.append(dest)
    return destinations


def parse_case_ids_arg(case_arg: Optional[str]) -> Optional[List[Union[int, str]]]:
    if not case_arg:
        return None
    parts = [item.strip() for item in case_arg.split(",") if item.strip()]
    return parts or None


def main(args: Optional[Sequence[str]] = None) -> None:
    case_arg = None
    force = False

    if args:
        case_arg = next((arg.split("=", 1)[1] for arg in args if arg.startswith("--cases=")), None)
        force = "--force" in args

    cases = parse_case_ids_arg(case_arg)
    download_cases(case_ids=cases, force=force)


if __name__ == "__main__":
    main(sys.argv[1:])


