"""Validate generated life-blog pages and publication-ready cnblogs drafts."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def life_article_pages() -> list[Path]:
    pages: list[Path] = []
    for source in sorted((ROOT / "blog-src" / "life").glob("*.md")):
        text = source.read_text(encoding="utf-8")
        date = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})\s*$", text, re.M)
        slug = re.search(r"^slug:\s*([^\s]+)\s*$", text, re.M)
        if date and slug:
            pages.append(ROOT / "blog" / date.group(1).replace("-", "/") / slug.group(1) / "index.html")
    return pages


LIFE_PAGES = [
    ROOT / "blog" / "index.html",
    ROOT / "blog" / "archives" / "index.html",
] + life_article_pages()


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str]] = []
        self.images = 0
        self.images_with_alt = 0
        self.h1 = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.refs.append(("href", values["href"] or ""))
        if tag in {"img", "script"} and values.get("src"):
            self.refs.append(("src", values["src"] or ""))
        if tag == "link" and values.get("href"):
            self.refs.append(("href", values["href"] or ""))
        if tag == "img":
            self.images += 1
            if values.get("alt", "").strip():
                self.images_with_alt += 1
        if tag == "h1":
            self.h1 += 1


def local_target(value: str) -> Path | None:
    parts = urlsplit(value)
    if parts.scheme or parts.netloc or value.startswith(("#", "mailto:", "javascript:")):
        return None
    path = unquote(parts.path)
    if not path.startswith("/"):
        return None
    target = ROOT / path.lstrip("/")
    if path.endswith("/"):
        target /= "index.html"
    return target


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def main() -> int:
    failures: list[str] = []
    for page in LIFE_PAGES:
        if not page.is_file():
            fail(f"missing page: {page.relative_to(ROOT)}", failures)
            continue
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        expected_h1 = 0 if page == ROOT / "blog" / "archives" / "index.html" else 1
        if parser.h1 != expected_h1:
            fail(f"{page.relative_to(ROOT)}: expected {expected_h1} h1, found {parser.h1}", failures)
        if parser.images != parser.images_with_alt:
            fail(f"{page.relative_to(ROOT)}: image without alt text", failures)
        for attr, value in parser.refs:
            target = local_target(value)
            if target is not None and not target.exists():
                fail(
                    f"{page.relative_to(ROOT)}: broken {attr}={value} -> {target.relative_to(ROOT)}",
                    failures,
                )

    cnblogs = sorted((ROOT / "cnblogs-drafts").glob("[0-9][0-9]-*.md"))
    if len(cnblogs) != 6:
        fail(f"expected 6 cnblogs drafts, found {len(cnblogs)}", failures)
    for draft in cnblogs:
        text = draft.read_text(encoding="utf-8")
        if len(re.sub(r"\s+", "", text)) < 1800:
            fail(f"{draft.relative_to(ROOT)}: draft is too short", failures)
        if not re.search(r"^status:\s*待发布\s*$", text, re.M):
            fail(f"{draft.relative_to(ROOT)}: missing draft publication status", failures)
        if "参考资料" not in text:
            fail(f"{draft.relative_to(ROOT)}: missing references", failures)
        for image in re.findall(r"!\[[^]]*\]\((/[^)]+)\)", text):
            target = local_target(image)
            if target is None or not target.exists():
                fail(f"{draft.relative_to(ROOT)}: broken image {image}", failures)

    if failures:
        print("BLOG OUTPUT CHECK: FAIL")
        for item in failures:
            print(f"- {item}")
        return 1
    print(f"BLOG OUTPUT CHECK: PASS ({len(LIFE_PAGES)} HTML pages, {len(cnblogs)} cnblogs drafts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
