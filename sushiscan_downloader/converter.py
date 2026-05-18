import os
import zipfile
from typing import List

import img2pdf
import py7zr


class Converter:
    @staticmethod
    def create_cbz(images: List[str], output_path: str):
        if len(images) == 0:
            return
        with zipfile.ZipFile(output_path, "w") as zf:
            for img in images:
                zf.write(img, os.path.basename(img))

    @staticmethod
    def create_cb7(images: List[str], output_path: str):
        if len(images) == 0:
            return
        with py7zr.SevenZipFile(output_path, "w") as zf:
            for img in images:
                zf.write(img, os.path.basename(img))

    @staticmethod
    def create_pdf(images: List[str], output_path: str):
        if len(images) == 0:
            return
        try:
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(images))
        except Exception as e:
            print(f"Error creating PDF: {e}")

    @staticmethod
    def create_epub(images: List[str], output_path: str, title: str):
        if len(images) == 0:
            return
        with zipfile.ZipFile(output_path, "w") as zf:
            zf.writestr("mimetype", "application/epub+zip")
            zf.writestr(
                "META-INF/container.xml",
                """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""",
            )

            manifest = []
            spine = []

            for i, img in enumerate(images):
                filename = os.path.basename(img)
                zf.write(img, f"OEBPS/images/{filename}")
                page_id = f"page_{i + 1}"
                manifest.append(
                    f'<item id="{page_id}" href="images/{filename}" media-type="image/jpeg"/>'
                )

                html_content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Page {i + 1}</title></head>
<body><img src="images/{filename}" style="max-width:100%;"/></body>
</html>"""
                zf.writestr(f"OEBPS/page_{i + 1}.xhtml", html_content)
                manifest.append(
                    f'<item id="xhtml_{i + 1}" href="page_{i + 1}.xhtml" media-type="application/xhtml+xml"/>'
                )
                spine.append(f'<itemref idref="xhtml_{i + 1}"/>')

            content_opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{title}</dc:title>
  </metadata>
  <manifest>
    {"".join(manifest)}
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="ncx">
    {"".join(spine)}
  </spine>
</package>"""
            zf.writestr("OEBPS/content.opf", content_opf)

            zf.writestr(
                "OEBPS/toc.ncx",
                f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="urn:uuid:12345"/></head>
  <docTitle><text>{title}</text></docTitle>
  <navMap/>
</ncx>""",
            )
