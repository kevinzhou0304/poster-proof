"""Command-line entry point for local image checks."""

import argparse
import json
from pathlib import Path

from poster_proof.audit import AuditOptions, audit_image


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a promotional image before delivery")
    parser.add_argument("image", type=Path, help="Local PNG, JPEG, TIFF, or other Pillow image")
    parser.add_argument("--min-width", type=int, default=0)
    parser.add_argument("--min-height", type=int, default=0)
    parser.add_argument("--require-rgb", action="store_true")
    parser.add_argument("--require-qr", action="store_true")
    parser.add_argument("--expect-qr", help="Expected QR payload; never written to the report")
    parser.add_argument(
        "--preview-width",
        type=int,
        action="append",
        dest="preview_widths",
        help="Check QR readability after reducing to this width; repeat as needed",
    )
    parser.add_argument("--json", type=Path, dest="json_path", help="Save a JSON report")
    args = parser.parse_args(argv)

    try:
        options = AuditOptions(
            min_width=args.min_width,
            min_height=args.min_height,
            require_rgb=args.require_rgb,
            require_qr=args.require_qr or args.expect_qr is not None,
            expected_qr_text=args.expect_qr,
            preview_widths=tuple(args.preview_widths or (1080, 720)),
        )
        report = audit_image(args.image, options)
        if args.json_path:
            args.json_path.write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 2

    print(f"{'PASS' if report['passed'] else 'FAIL'}: {args.image}")
    for check in report["checks"]:
        print(f"  {'PASS' if check['passed'] else 'FAIL'} {check['code']}: {check['detail']}")
    for preview in report["qr_previews"]:
        print(f"  QR at {preview['width']}px: {preview['decoded_count']} decoded")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
