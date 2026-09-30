import json
from pathlib import Path

from PIL import Image

from poster_proof.cli import main


def test_cli_writes_json_report_and_returns_failure_for_failed_checks(
    tmp_path: Path, capsys
) -> None:
    image = tmp_path / "poster.png"
    output = tmp_path / "report.json"
    Image.new("RGB", (640, 900), "white").save(image)

    exit_code = main([str(image), "--min-width", "1080", "--json", str(output)])

    assert exit_code == 1
    assert output.exists()
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["passed"] is False
    assert report["image"]["width"] == 640
    assert "FAIL" in capsys.readouterr().out
