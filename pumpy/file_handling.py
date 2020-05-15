# coding: utf-8

import csv
from pathlib import Path
from typing import List


def process_file(path: Path) -> List[str]:
    list_ids: List[str] = list()
    if path.suffix == ".csv":
        pass

    elif path.suffix == ".tsv":
        pass
    elif path.suffix == ".txt":
        with open(path, "r", encoding="utf-8") as ids:
            for id in ids:
                list_ids.append(id.strip())

    return list_ids


if __name__ == "__main__":
    process_file(Path("/home/kyd/Téléchargements/tyendinaga-ids.txt"))
