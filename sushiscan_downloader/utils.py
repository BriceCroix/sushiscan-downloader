from typing import List


def sanitize_filename(name: str) -> str:
    return "".join(
        [c for c in name if c.isalpha() or c.isdigit() or c in " ._-()[]"]
    ).strip()


def parse_selection(selection: str, available_ids: List[str]) -> List[str]:
    if not selection or selection.lower() == "all":
        return available_ids

    selected = set()
    parts = selection.split(",")

    import re

    def extract_number(s):
        match = re.search(r"(\d+(?:\.\d+)?)", str(s))
        if match:
            return float(match.group(1))
        return None

    def is_match(target_str, id_str):
        if target_str == id_str:
            return True

        target_val = extract_number(target_str)
        id_val = extract_number(id_str)

        if target_val is not None and id_val is not None:
            return target_val == id_val
        return False

    for part in parts:
        part = part.strip()
        if "-" in part:
            try:
                start, end = part.split("-")
                start_num = float(start)
                end_num = float(end)
                for item_id in available_ids:
                    val = extract_number(item_id)
                    if val is not None and start_num <= val <= end_num:
                        selected.add(item_id)
            except ValueError:
                pass
        else:
            for item_id in available_ids:
                if is_match(part, item_id):
                    selected.add(item_id)

    result = [id for id in available_ids if id in selected]
    return result
