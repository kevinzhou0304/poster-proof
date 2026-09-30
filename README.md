# Poster Proof

An offline command-line checker for promotional images. It reports pixel dimensions, color mode, whether an ICC profile is embedded, and whether a QR code can still be decoded after the image is reduced to sharing sizes. Image files stay on your computer.

This is an early public project, version 0.1.0. It is not a substitute for a physical print proof or a scan with the intended phone and app.

## Install

Requires Python 3.10 or newer.

```bash
python -m pip install .
```

For development and tests:

```bash
python -m pip install -e ".[test]"
python -m pytest
```

## Check an image

```bash
poster-proof poster.png --min-width 1080 --min-height 1920 --require-rgb
```

Check a QR code at the source size and at two smaller share widths:

```bash
poster-proof poster.png --require-qr --preview-width 1080 --preview-width 720 --json report.json
```

Confirm a particular QR destination without including its text in the output:

```bash
poster-proof poster.png --expect-qr "https://example.org/event" --json report.json
```

The command exits with `0` when all requested checks pass, `1` when a check fails, and `2` when an image or option cannot be read. The JSON report records only the image filename, not its full local path. It records whether the expected QR text matched, but does not record the decoded text or the expected value. Preview widths at or above the source width are omitted because they are not reductions.

## 中文说明

Poster Proof 是离线宣传图片交付检查工具。它核对像素尺寸、颜色模式、是否带有 ICC 配置文件，并测试二维码在原图和缩小预览尺寸下能否解码。图片不会上传。示例：

```bash
poster-proof 海报.png --min-width 1080 --min-height 1920 --require-rgb --require-qr --preview-width 720 --json 检查结果.json
```

`--expect-qr` 可以检查二维码内容是否与指定网址相符；检查报告只记录图片文件名，不记录完整本机路径，也不会保存二维码原文。二维码通过软件解码，仍应在最终投放设备上实测扫码。印刷品还需根据实际设备和材料打样。

## Scope and limitations

- The checker does not transform, crop, recolor, or upload the input image.
- An embedded ICC profile is reported as metadata; the tool does not judge whether it matches a printer or display.
- QR decoding is based on OpenCV. A successful result is evidence of machine readability at the tested pixel sizes, not a guarantee under every camera, screen, lighting, or print condition.
- Only one image is checked per command. Batch support may be added after real usage feedback.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and reproducible sample images without private information are welcome.

## License

MIT. See [LICENSE](LICENSE).
