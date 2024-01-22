import copy
import json
import sys
from typing import Any, Dict, List

from dateutil import parser

RETCODE: int = 0


def load_json_file(fpath: str) -> List[Dict[str, Any]]:
    with open(fpath, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    global RETCODE

    games_orig: List[Dict[str, Any]] = load_json_file("manifest.json")
    games_new: List[Dict[str, Any]] = load_json_file("manifest-new.json")

    # merge edits
    idx = 0
    print(len(games_orig))
    edited: List[str] = []
    for game in games_orig:
        for game_new in games_new:
            if game["slug"] == game_new["slug"]:
                if game != game_new:
                    print(
                        f"{game['slug']} differs from manifest, checking date..."
                    )
                    old_time = parser.parse(game["dateChanged"])
                    new_time = parser.parse(game_new["dateChanged"])
                    if new_time > old_time:
                        print("changes for entry are newer! replacing...")
                        games_orig[idx] = copy.deepcopy(game_new)
                        edited.append(game["slug"])
        idx += 1

    # merge new items
    for game_new in games_new:
        if (game_new not in games_orig) and (game_new["slug"] not in edited):
            print(f"{game_new['slug']} not in manifest, merging...")
            games_orig.append(copy.deepcopy(game_new))

    # delete items that are missing from the new manifest
    idx = 0
    for game in games_orig:
        if game not in games_new:
            print(f"{game['slug']} is not in new manifest, removing...")
            games_orig.pop(idx)
        idx += 1

    with open("manifest-merged.json", "w", encoding="utf-8") as f:
        json.dump(games_orig, f)
    return RETCODE


if __name__ == "__main__":
    sys.exit(main())
