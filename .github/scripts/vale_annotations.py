#!/usr/bin/env python3
"""Turn Vale's JSON output into GitHub workflow annotations.

Usage: vale --output=JSON --no-exit <files> > vale.json
       python3 vale_annotations.py vale.json [more.json ...]   ("-" for stdin)

Several outputs are merged before annotating.

Prints one annotation per alert (error -> ::error, warning -> ::warning,
suggestion -> ::notice) and a summary line. Exit 0 when there are no errors,
1 when Vale reported an error-level alert, 2 when Vale's output could not be
read (malformed or too deeply nested JSON, or Vale's own runtime error).
Standard library only; every step is linear in the size of the input.
"""

import json
import sys

LEVELS = {"error": "error", "warning": "warning", "suggestion": "notice"}


def escape_data(text):
    """Escape an annotation message (GitHub's workflow-command data rules)."""
    return str(text).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def escape_property(text):
    """Escape an annotation property value (file, title): also ':' and ','."""
    return escape_data(text).replace(":", "%3A").replace(",", "%2C")


def _positive_int(value, default=1):
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else default


def annotations(results):
    """Yield (severity, file, line, col, check, message) for each alert, sorted by file then line."""
    rows = []
    for path, alerts in results.items():
        if not isinstance(alerts, list):
            raise ValueError(f"alerts for {path!r} are not a list")
        for a in alerts:
            if not isinstance(a, dict):
                raise ValueError(f"an alert for {path!r} is not an object")
            span = a.get("Span")
            col = _positive_int(span[0]) if isinstance(span, list) and span else 1
            severity = a.get("Severity") if a.get("Severity") in LEVELS else "warning"
            rows.append((str(path), _positive_int(a.get("Line")), col, severity,
                         str(a.get("Check", "Vale")), str(a.get("Message", ""))))
    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    for path, line, col, severity, check, message in rows:
        yield severity, path, line, col, check, message


class ValeError(ValueError):
    pass


def read_results(path):
    """Return one Vale JSON output as {path: [alerts]}; raise ValueError for Vale's own error."""
    text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    results = json.loads(text)
    if not isinstance(results, dict):
        raise ValueError("Vale's output is not a JSON object")
    if "Code" in results and "Text" in results and not isinstance(results.get("Text"), list):
        raise ValeError(f"{results['Code']} {results['Text']}")
    return results


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("usage: vale_annotations.py <vale.json | -> [more.json ...]", file=sys.stderr)
        return 2
    merged = {}
    try:
        for path in argv:
            for file, alerts in read_results(path).items():
                if not isinstance(alerts, list):
                    raise ValueError(f"alerts for {file!r} are not a list")
                merged.setdefault(file, []).extend(alerts)
        rows = list(annotations(merged))
    except ValeError as e:
        print(f"::error title=Vale::{escape_data(e)}")
        return 2
    except (OSError, ValueError, RecursionError) as e:
        print(f"::error title=Vale::could not read Vale's JSON output: {escape_data(e)}")
        return 2

    counts = {"error": 0, "warning": 0, "suggestion": 0}
    for severity, path, line, col, check, message in rows:
        counts[severity] += 1
        print(f"::{LEVELS[severity]} file={escape_property(path)},line={line},col={col},"
              f"title={escape_property(check)}::{escape_data(message)}")

    def plural(n, word):
        return f"{n} {word}{'' if n == 1 else 's'}"
    print(f"Vale: {plural(counts['error'], 'error')}, {plural(counts['warning'], 'warning')}, "
          f"{plural(counts['suggestion'], 'suggestion')}.")
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
