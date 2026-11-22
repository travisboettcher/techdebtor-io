"""vale_annotations.py turns Vale's JSON output into GitHub workflow annotations."""

import io
import json
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vale_annotations as va  # noqa: E402


def alert(check="Direct.Hedging", severity="warning", line=3, span=(5, 10), message="Drop the hedge 'try to'."):
    return {"Check": check, "Severity": severity, "Line": line, "Span": list(span), "Message": message,
            "Match": "try to", "Link": "", "Description": "", "Action": {"Name": "", "Params": None}}


def run(data, tmp_path, capsys, as_text=None):
    p = tmp_path / "vale.json"
    p.write_text(as_text if as_text is not None else json.dumps(data))
    code = va.main([str(p)])
    return code, capsys.readouterr().out


def test_warnings_become_warning_annotations_and_pass(tmp_path, capsys):
    code, out = run({"README.md": [alert()]}, tmp_path, capsys)
    assert code == 0
    assert "::warning file=README.md,line=3,col=5,title=Direct.Hedging::Drop the hedge 'try to'." in out.splitlines()


def test_an_error_fails_and_suggestions_are_notices(tmp_path, capsys):
    data = {"a.md": [alert(severity="error", check="Vale.Repetition", message="'the' is repeated!")],
            "b.md": [alert(severity="suggestion")]}
    code, out = run(data, tmp_path, capsys)
    assert code == 1
    assert "::error file=a.md,line=3,col=5,title=Vale.Repetition::'the' is repeated!" in out
    assert "::notice file=b.md," in out
    assert "1 error, 0 warnings, 1 suggestion" in out


def test_no_alerts_passes(tmp_path, capsys):
    code, out = run({}, tmp_path, capsys)
    assert code == 0 and "0 errors, 0 warnings, 0 suggestions" in out


def test_output_is_sorted_by_file_then_line(tmp_path, capsys):
    data = {"z.md": [alert(line=1)], "a.md": [alert(line=9), alert(line=2)]}
    _, out = run(data, tmp_path, capsys)
    lines = [l for l in out.splitlines() if l.startswith("::")]
    assert [l.split(",")[0:2] for l in lines] == [["::warning file=a.md", "line=2"],
                                                   ["::warning file=a.md", "line=9"],
                                                   ["::warning file=z.md", "line=1"]]


def test_workflow_command_injection_is_escaped(tmp_path, capsys):
    # A file name or message must never end the annotation early or start a new workflow command.
    data = {"evil,line=1::x.md": [alert(message="first\n::error::injected\r%0A done", check="A:B,C")]}
    _, out = run(data, tmp_path, capsys)
    lines = out.splitlines()
    annotations = [l for l in lines if l.startswith("::")]
    assert len(annotations) == 1
    a = annotations[0]
    assert a.startswith("::warning file=evil%2Cline=1%3A%3Ax.md,line=3,col=5,title=A%3AB%2CC::")
    assert a.endswith("::first%0A::error::injected%0D%250A done")
    assert not any(l.startswith("::error") for l in lines)


def test_missing_or_bad_fields_fall_back_safely(tmp_path, capsys):
    data = {"a.md": [{"Check": "X.Y", "Severity": "bogus", "Line": "7; rm -rf /", "Message": "m"}]}
    code, out = run(data, tmp_path, capsys)
    assert code == 0
    assert "::warning file=a.md,line=1,col=1,title=X.Y::m" in out


def test_vale_runtime_error_fails_with_its_message(tmp_path, capsys):
    code, out = run({"Code": "E100", "Text": "Runtime error: bad config"}, tmp_path, capsys)
    assert code == 2
    assert "::error title=Vale::E100 Runtime error: bad config" in out


@pytest.mark.parametrize("text", ["", "not json", "[1, 2]", '{"a.md": "x"}', '{"a.md": [1]}'])
def test_unreadable_output_fails(tmp_path, capsys, text):
    code, out = run(None, tmp_path, capsys, as_text=text)
    assert code == 2 and "::error title=Vale::" in out


def test_reads_stdin_with_dash(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"a.md": [alert()]})))
    assert va.main(["-"]) == 0
    assert "::warning file=a.md" in capsys.readouterr().out


def test_escaping_is_linear_time():
    big = "%:,\r\n" * 400_000
    start = time.perf_counter()
    va.escape_property(big)
    va.escape_data(big)
    assert time.perf_counter() - start < 2


def test_deeply_nested_json_fails_cleanly(tmp_path, capsys):
    code, out = run(None, tmp_path, capsys, as_text="[" * 200_000 + "]" * 200_000)
    assert code == 2 and "::error title=Vale::" in out


def test_several_outputs_are_merged(tmp_path, capsys):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    a.write_text(json.dumps({"x.md": [alert(line=4)]}))
    b.write_text(json.dumps({"x.md": [alert(line=2, severity="error")], "y.md": [alert()]}))
    assert va.main([str(a), str(b)]) == 1
    lines = [l for l in capsys.readouterr().out.splitlines() if l.startswith("::")]
    assert [l.split(",")[:2] for l in lines] == [["::error file=x.md", "line=2"], ["::warning file=x.md", "line=4"],
                                                 ["::warning file=y.md", "line=3"]]


def test_a_vale_error_in_any_output_fails(tmp_path, capsys):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    a.write_text(json.dumps({}))
    b.write_text(json.dumps({"Code": "E201", "Text": "bad"}))
    assert va.main([str(a), str(b)]) == 2
