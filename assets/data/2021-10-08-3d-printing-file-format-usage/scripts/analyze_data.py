import json
from copy import copy
from datetime import date, datetime
from pathlib import Path

FILETYPES = [
    ".stl",
    ".scad",
    ".obj",
    ".step",
    ".stp",
    ".sldprt",
    ".skp",
    ".f3d",
    ".fcstd",
    ".dxf",
    ".gcode",
    ".ipt",
    ".3mf",
    ".blend",
    ".123dx",
    ".amf",
]


def _pretty_number(num):
    return f"{num:,}"


def _get_suffix(filename: str):
    return "." + filename.split(".", 1)[-1]


def _get_suffixes(filename):
    _file = Path(filename)
    _suffix = _file.suffix.strip()
    if _suffix == "":
        if _suffix.startswith("."):
            _suffix = filename
        else:
            raise ValueError()
    _suffixes = set([suf.lower() for suf in _file.suffixes] + [_suffix.lower()])

    return _suffixes


def _increment_entry(dict_, key):
    if key not in dict_:
        dict_[key] = 0
    dict_[key] += 1


def file_analysis(file_data):
    data = file_data["data"]
    _statistics = {
        "suffix_raw": {},
        "suffixes_unified": {},
        "combinations_of_filetypes": {},
        "object_w_type_file": {t: 0 for t in FILETYPES},
        "object_wo_known_filetype": [],
    }
    statistics = {k: dict() for k in FILETYPES}
    statistics["total number of files"] = _pretty_number(
        file_data["nr_thingiverse_files"] + file_data["nr_myminifactory_files"]
    )

    for object_files in data:
        _all_cleaned_suffixes = []

        for filename, _ in object_files:
            try:
                _raw_suffix = _get_suffix(filename)
                _increment_entry(_statistics["suffix_raw"], _raw_suffix)

                _cleaned_suffixes = _get_suffixes(filename)
                for _cleaned_suffix in _cleaned_suffixes:
                    _increment_entry(_statistics["suffixes_unified"], _cleaned_suffix)
                _all_cleaned_suffixes += _cleaned_suffixes

            except ValueError:
                continue

        _all_cleaned_suffixes = list(set(_all_cleaned_suffixes))

        _has_any_known_filetype = False
        for suffix in _all_cleaned_suffixes:
            for filetype in FILETYPES:
                if filetype == suffix:
                    _has_any_known_filetype = True
                    _statistics["object_w_type_file"][filetype] += 1
                    break

        if not _has_any_known_filetype:
            _statistics["object_wo_known_filetype"].append(_all_cleaned_suffixes)

        _increment_entry(
            _statistics["combinations_of_filetypes"],
            "".join(sorted(list(set(_all_cleaned_suffixes)))),
        )

    _statistics["object_unknown_filetype_suffixes"] = {}
    for suffixes in _statistics["object_wo_known_filetype"]:
        for suffix in suffixes:
            _increment_entry(_statistics["object_unknown_filetype_suffixes"], suffix)

    for stat in _statistics:
        if isinstance(_statistics[stat], dict):
            _statistics[stat] = {
                k: v for k, v in sorted(_statistics[stat].items(), key=lambda item: -item[1])
            }

    for filetype in FILETYPES:
        stats = statistics[filetype]
        stats["ft occurs in this many objects"] = _pretty_number(
            _statistics["object_w_type_file"][filetype]
        )
        stats["times ft occurs in total"] = _pretty_number(
            _statistics["suffixes_unified"][filetype]
        )
        stats["times ft occurs on its own"] = _pretty_number(
            _statistics["combinations_of_filetypes"][filetype]
        )
        i = 0
        stats["top 10 combinations of ft with others"] = {}
        for combination, count in _statistics["combinations_of_filetypes"].items():
            if filetype in combination:
                i += 1
                stats["top 10 combinations of ft with others"][combination] = _pretty_number(count)
                if i >= 10:
                    break

    statistics["top 10 filetypes of objects that don't contain any known filetype"] = {
        f_type: _pretty_number(count)
        for i, (f_type, count) in enumerate(_statistics["object_unknown_filetype_suffixes"].items())
        if i < 10
    }

    with open("data/file_analysis_raw.json", "w") as file:
        json.dump(_statistics, file, indent=4)

    with open("data/file_analysis.json", "w") as file:
        json.dump(statistics, file, indent=4)


def format_uploads_per_day(data):
    # same as format_uploads_per_day_per_object but doesn't ignore duplicates
    formats_over_time = {}

    for object_files in data:
        for filename, timestamp in object_files:
            try:
                _suffixes = _get_suffixes(filename)
            except ValueError:
                continue

            if timestamp is None:
                continue

            _date = date.fromtimestamp(timestamp).isoformat()
            if _date not in formats_over_time:
                formats_over_time[_date] = {t: 0 for t in FILETYPES}

            for ext in FILETYPES:
                if ext in _suffixes:
                    formats_over_time[_date][ext] += 1

    with open("data/format_uploads_per_day.json", "w") as file:
        json.dump(formats_over_time, file, indent=4)


def format_uploads_per_day_per_object(data):
    formats_over_time = {}

    for object_files in data:
        _distinct_entries = set()

        # get all models for an entry
        # ignore models where the date and filetype are the same (duplicates)
        for filename, timestamp in object_files:
            try:
                _suffixes = _get_suffixes(filename)
            except ValueError:
                continue

            if timestamp is None:
                continue

            _date = date.fromtimestamp(timestamp).isoformat()
            for ext in FILETYPES:
                if ext in _suffixes:
                    _distinct_entries.add((_date, ext))

        # count the gathered files in the overall dict
        for _date, ext in _distinct_entries:
            if _date not in formats_over_time:
                formats_over_time[_date] = {t: 0 for t in FILETYPES}
            formats_over_time[_date][ext] += 1

    with open("data/format_uploads_per_day_per_object.json", "w") as file:
        json.dump(formats_over_time, file, indent=4)


def number_of_files_per_object(data):
    formats_per_object = []

    for object_files in data:
        res = {}
        for filename, _ in object_files:
            try:
                _suffixes = _get_suffixes(filename)
            except ValueError:
                continue

            for ft in FILETYPES:
                if ft in _suffixes:
                    _increment_entry(res, ft)
        formats_per_object.append(res)

    nr_of_files_per_object = {}

    for ft in FILETYPES:
        nr_of_files_per_object[ft] = {
            "objects_with_this_type": 0,
            "total_nr_files_of_objects_with_at_least_one": 0,
        }
        for entry in formats_per_object:
            if ft in entry:
                nr_of_files_per_object[ft]["objects_with_this_type"] += 1
                nr_of_files_per_object[ft]["total_nr_files_of_objects_with_at_least_one"] += entry[
                    ft
                ]

    for _, infos in nr_of_files_per_object.items():
        infos["average_number_of_files_per_object"] = round(
            infos["total_nr_files_of_objects_with_at_least_one"] / infos["objects_with_this_type"],
            ndigits=2,
        )

    with open("data/number_of_files_per_object.json", "w") as file:
        json.dump(nr_of_files_per_object, file, indent=4)


def top_filetypes_wo_stl(data):

    res = {}
    for object_files in data:
        suffixes = set()
        for filename, _ in object_files:
            try:
                suffixes.update(_get_suffixes(filename))
            except ValueError:
                continue

        for ft in suffixes:
            if ".stl" not in suffixes:
                _increment_entry(res, ft)

    with open("data/number_of_files_in_objs_wo_stl.json", "w") as file:
        json.dump(
            {
                suffix: count
                for suffix, count in sorted(
                    res.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
                if count > 10
            },
            file,
            indent=4,
        )


def multiple_suffixes(data):
    interesting_suffixes = {ft: {"occurrences": 0, "occures_with": {}} for ft in FILETYPES}

    mult_occs = {}
    for suffix, occurrences in data.items():
        if len(suffix.split(".")) > 2:
            mult_occs[suffix] = occurrences
            for i_suf in interesting_suffixes:
                if i_suf in suffix:
                    interesting_suffixes[i_suf]["occurrences"] += occurrences
                    occures_with = suffix.replace(i_suf, "")
                    if occures_with not in interesting_suffixes[i_suf]["occures_with"]:
                        interesting_suffixes[i_suf]["occures_with"][occures_with] = 0
                    interesting_suffixes[i_suf]["occures_with"][occures_with] += 1

    total_nr_files = sum(mult_occs.values())
    for _, infos in interesting_suffixes.items():
        infos["rel_occurrences"] = round(infos["occurrences"] / total_nr_files * 100, ndigits=2)
        infos["occures_with"] = {
            other_suffixes: count
            for other_suffixes, count in sorted(
                infos["occures_with"].items(),
                key=lambda item: item[1],
                reverse=True,
            )
            # if count > 1
        }
    interesting_suffixes["total_nr_files"] = total_nr_files

    with open("data/multiple_occurrences.json", "w") as file:
        json.dump(interesting_suffixes, file, indent=4)


def main():
    with open("data/extracted_data.json") as file:
        file_data = json.load(file)
        file_analysis(file_data)
        format_uploads_per_day(file_data["data"])
        format_uploads_per_day_per_object(file_data["data"])
        number_of_files_per_object(file_data["data"])
        top_filetypes_wo_stl(file_data["data"])

    with open("data/file_analysis_raw.json") as file:
        file_data = json.load(file)
        multiple_suffixes(file_data["suffix_raw"])


if __name__ == "__main__":
    main()
