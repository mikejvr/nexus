def walk_sorted(path):
    return sorted(Path(path).rglob("*"), key=lambda p: str(p))