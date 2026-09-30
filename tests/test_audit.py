from pathlib import Path

import pytest
import qrcode
from PIL import Image

from poster_proof.audit import AuditOptions, audit_image


def make_poster(path: Path, *, mode: str = "RGB", with_qr: bool = True) -> None:
    poster = Image.new(mode, (1200, 1800), "white")
    if with_qr:
        code = qrcode.make("https://example.org/event").convert("RGB")
        code = code.resize((360, 360), Image.Resampling.NEAREST)
        poster.paste(code, (750, 1300))
    poster.save(path)


def test_good_poster_passes_and_qr_decodes_at_preview_sizes(tmp_path: Path) -> None:
    path = tmp_path / "poster.png"
    make_poster(path)

    report = audit_image(
        path,
        AuditOptions(
            min_width=1000,
            min_height=1700,
            require_rgb=True,
            require_qr=True,
            expected_qr_text="https://example.org/event",
            preview_widths=(1080, 720),
        ),
    )

    assert report["passed"] is True
    assert report["image"]["width"] == 1200
    assert report["image"]["height"] == 1800
    assert [item["width"] for item in report["qr_previews"]] == [1200, 1080, 720]
    assert all(item["decoded_count"] >= 1 for item in report["qr_previews"])
    assert all(item["expected_match"] is True for item in report["qr_previews"])
    assert "https://example.org/event" not in str(report)


def test_report_records_filename_without_local_directory(tmp_path: Path) -> None:
    path = tmp_path / "poster.png"
    make_poster(path)

    report = audit_image(path, AuditOptions())

    assert report["path"] == path.name
    assert str(tmp_path) not in str(report)


def test_dimension_and_color_failures_are_reported(tmp_path: Path) -> None:
    path = tmp_path / "small-gray.png"
    Image.new("L", (400, 600), "white").save(path)

    report = audit_image(
        path,
        AuditOptions(min_width=1000, min_height=1700, require_rgb=True),
    )

    assert report["passed"] is False
    assert {item["code"] for item in report["checks"] if not item["passed"]} == {
        "dimensions",
        "rgb_mode",
    }


def test_missing_qr_fails_when_required(tmp_path: Path) -> None:
    path = tmp_path / "no-code.png"
    make_poster(path, with_qr=False)

    report = audit_image(path, AuditOptions(require_qr=True, preview_widths=(720,)))

    assert report["passed"] is False
    assert [item["decoded_count"] for item in report["qr_previews"]] == [0, 0]
    assert any(item["code"] == "qr_readable" and not item["passed"] for item in report["checks"])


def test_wrong_expected_qr_is_reported_without_disclosing_payload(tmp_path: Path) -> None:
    path = tmp_path / "poster.png"
    make_poster(path)

    report = audit_image(
        path,
        AuditOptions(expected_qr_text="https://example.org/wrong", preview_widths=(720,)),
    )

    assert report["passed"] is False
    assert any(
        item["code"] == "qr_matches_expected" and not item["passed"]
        for item in report["checks"]
    )
    assert "https://example.org/event" not in str(report)
    assert "https://example.org/wrong" not in str(report)


def test_invalid_image_raises_clear_error(tmp_path: Path) -> None:
    path = tmp_path / "broken.png"
    path.write_text("not an image", encoding="utf-8")

    with pytest.raises(ValueError, match="Cannot read image"):
        audit_image(path, AuditOptions())
