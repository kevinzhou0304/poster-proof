from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


@dataclass(frozen=True)
class AuditOptions:
    min_width: int = 0
    min_height: int = 0
    require_rgb: bool = False
    require_qr: bool = False
    expected_qr_text: str | None = None
    preview_widths: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.min_width < 0 or self.min_height < 0:
            raise ValueError("Minimum dimensions cannot be negative")
        if any(width <= 0 for width in self.preview_widths):
            raise ValueError("Preview widths must be positive")


def _decoded_qr_texts(image: Image.Image) -> set[str]:
    pixels = cv2.cvtColor(np.asarray(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()
    found, values, _, _ = detector.detectAndDecodeMulti(pixels)
    decoded = {value for value in values if value} if found else set()
    if not decoded:
        value, _, _ = detector.detectAndDecode(pixels)
        if value:
            decoded.add(value)
    return decoded


def _check(code: str, passed: bool, detail: str) -> dict:
    return {"code": code, "passed": passed, "detail": detail}


def audit_image(path: Path, options: AuditOptions) -> dict:
    path = Path(path)
    try:
        with Image.open(path) as source:
            source.verify()
        with Image.open(path) as source:
            image_format = source.format
            has_icc_profile = bool(source.info.get("icc_profile"))
            image = ImageOps.exif_transpose(source)
            image.load()
    except (OSError, UnidentifiedImageError, ValueError) as exc:
        raise ValueError(f"Cannot read image: {path}") from exc

    width, height = image.size
    checks = [
        _check(
            "dimensions",
            width >= options.min_width and height >= options.min_height,
            f"{width}x{height}; minimum {options.min_width}x{options.min_height}",
        )
    ]
    if options.require_rgb:
        checks.append(_check("rgb_mode", image.mode == "RGB", f"Mode: {image.mode}"))

    previews = []
    if options.require_qr or options.expected_qr_text is not None:
        widths = [width] + sorted(
            {item for item in options.preview_widths if item < width}, reverse=True
        )
        for preview_width in widths:
            preview = (
                image
                if preview_width == width
                else image.resize(
                    (preview_width, round(height * preview_width / width)),
                    Image.Resampling.LANCZOS,
                )
            )
            decoded = _decoded_qr_texts(preview)
            previews.append(
                {
                    "width": preview_width,
                    "decoded_count": len(decoded),
                    "expected_match": (
                        options.expected_qr_text in decoded
                        if options.expected_qr_text is not None
                        else None
                    ),
                }
            )

        checks.append(
            _check(
                "qr_readable",
                all(item["decoded_count"] > 0 for item in previews),
                "At least one QR code must decode at every tested width",
            )
        )
        if options.expected_qr_text is not None:
            checks.append(
                _check(
                    "qr_matches_expected",
                    all(item["expected_match"] for item in previews),
                    "Expected QR content must decode at every tested width",
                )
            )

    return {
        "path": path.name,
        "passed": all(item["passed"] for item in checks),
        "image": {
            "format": image_format,
            "width": width,
            "height": height,
            "mode": image.mode,
            "icc_profile_embedded": has_icc_profile,
        },
        "checks": checks,
        "qr_previews": previews,
    }
