# Design note

Poster Proof is a small, offline preflight tool for one exported promotional image at a time. Pillow opens and checks the image, applies EXIF orientation, and reads dimensions, mode, and ICC metadata. OpenCV decodes QR codes from the source image and any requested smaller widths. The command reports checks in text and optionally JSON; it never saves decoded QR payloads or alters the input. The first version deliberately avoids printer-profile validation, automated visual judgment, and batch crawling.
