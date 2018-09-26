def remove_comments(line: str) -> str:
    return line.split("#")[0].strip()
