"""Use PyYAML if installed; else a tiny parser for this repo's simple YAML (maps, lists, scalars)."""
try:
    from yaml import safe_load  # noqa: F401
except ImportError:
    def _scalar(v):
        v = v.split(" #")[0].strip()
        if v in ("null", "~", ""): return None
        if v in ("true", "false"): return v == "true"
        for t in (int, float):
            try: return t(v)
            except ValueError: pass
        return v.strip("'\"")

    def safe_load(text):
        root = {}; stack = [(-1, root)]
        lines = [l for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
        for i, l in enumerate(lines):
            ind = len(l) - len(l.lstrip()); s = l.strip()
            while stack[-1][0] >= ind: stack.pop()
            parent = stack[-1][1]
            if s.startswith("- "):
                parent.append(_scalar(s[2:])); continue
            k, _, v = s.partition(":")
            if v.split(" #")[0].strip():
                parent[k] = _scalar(v)
            else:
                nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
                parent[k] = [] if nxt.startswith("- ") else {}
                stack.append((ind, parent[k]))
        return root
