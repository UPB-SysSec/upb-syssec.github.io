import json
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

data = []


def _extract_thingiverse(thing: dict):
    def parse_time(timestr):
        try:
            return (
                datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
                .replace(tzinfo=timezone.utc)
                .timestamp()
            )
        except (ValueError, TypeError):
            return

    _thing = [(file.get("name"), parse_time(file.get("date"))) for file in thing.get("files", [])]
    data.append(_thing)


def _extract_myminifactory(thing: dict):
    def parse_time(timestr):
        try:
            return datetime.fromisoformat(timestr).replace(tzinfo=timezone.utc).timestamp()
        except (ValueError, TypeError):
            return

    _thing = [
        (file.get("filename"), parse_time(file.get("created_at")))
        for file in thing.get("files", {}).get("items", [])
    ]
    data.append(_thing)


def _extract(filename, extract_function):
    success_opens = 0
    failed_opens = 0
    with ZipFile(filename) as zip_file:
        for name in zip_file.namelist():
            with zip_file.open(name) as file:
                try:
                    extract_function(json.load(file))
                    success_opens += 1
                except (json.decoder.JSONDecodeError, OSError):
                    # there are some incomplete files because the download was aborted
                    failed_opens += 1

    return (success_opens, failed_opens)


def main():

    failed_opens = 0

    nr_thingiverse_files, failed_opens_thingiverse = _extract(
        "data/thingiverse.zip", _extract_thingiverse
    )
    failed_opens += failed_opens_thingiverse

    nr_myminifactory_files, failed_opens_myminifactory = _extract(
        "data/myminifactory.zip", _extract_myminifactory
    )
    failed_opens += failed_opens_myminifactory

    with open("data/extracted_data.json", "w") as file:
        json.dump(
            {
                "data": data,
                "failed_opens": failed_opens,
                "nr_thingiverse_files": nr_thingiverse_files,
                "nr_myminifactory_files": nr_myminifactory_files,
            },
            file,
        )


if __name__ == "__main__":
    main()
