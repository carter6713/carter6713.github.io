"""Build life posts with the site's existing Hexo Fluid 1.9.9 markup."""

from __future__ import annotations

import html
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "blog-src" / "life"
BLOG = ROOT / "blog"
ARTICLE_TEMPLATE = BLOG / "2026" / "08" / "11" / "我的个人主页搭建记录" / "index.html"
INDEX_START = "<!-- LIFE_POSTS_START -->"
INDEX_END = "<!-- LIFE_POSTS_END -->"
ARCHIVE_START = "<!-- LIFE_ARCHIVE_START -->"
ARCHIVE_END = "<!-- LIFE_ARCHIVE_END -->"


def clean_text(value: str) -> str:
    """Keep generated HTML diff-friendly without changing Fluid markup."""
    return re.sub(r"(?:\r?\n)+$", "\n", re.sub(r"[ \t]+(?=\r?$)", "", value, flags=re.M))


def parse_post(path: Path) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not match:
        raise ValueError(f"Missing front matter: {path}")
    meta: dict[str, object] = {}
    for line in match.group(1).splitlines():
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    meta["tags"] = [tag.strip() for tag in str(meta.get("tags", "")).split(",") if tag.strip()]
    meta["markdown"] = match.group(2).strip()
    meta["body"] = markdown.markdown(
        str(meta["markdown"]),
        extensions=["extra", "sane_lists"],
        output_format="html5",
    )
    return meta


def post_url(post: dict[str, object]) -> str:
    return f"/blog/{str(post['date']).replace('-', '/')}/{post['slug']}/"


def localized_date(date: str) -> str:
    parsed = datetime.strptime(date, "%Y-%m-%d")
    return f"{parsed.year}年{parsed.month}月{parsed.day}日"


def render_tags(tags: list[str], css_class: str = "") -> str:
    class_attr = f' class="{css_class}"' if css_class else ""
    return "\n".join(
        f'        <a href="/blog/tags/"{class_attr}>#{html.escape(tag)}</a>' for tag in tags
    )


def render_article(template: str, post: dict[str, object]) -> str:
    title = str(post["title"])
    summary = str(post["summary"])
    date = str(post["date"])
    cover = str(post["cover"])
    tags = list(post["tags"])
    url = post_url(post)
    absolute_url = f"https://carter6713.github.io{url}index.html"
    published = f"{date}T00:00:00.000Z"
    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    text_count = len(re.sub(r"\s+", "", re.sub(r"!\[[^]]*\]\([^)]+\)", "", str(post["markdown"]))))
    minutes = max(1, math.ceil(text_count / 300))

    result = template
    replacements = {
        r'<meta name="description" content="[^"]*">': f'<meta name="description" content="{html.escape(summary)}">',
        r'<meta property="og:title" content="[^"]*">': f'<meta property="og:title" content="{html.escape(title)}">',
        r'<meta property="og:url" content="[^"]*">': f'<meta property="og:url" content="{absolute_url}">',
        r'<meta property="og:description" content="[^"]*">': f'<meta property="og:description" content="{html.escape(summary)}">',
        r'<meta property="og:image" content="[^"]*">': f'<meta property="og:image" content="https://carter6713.github.io{cover}">',
        r'<meta property="article:published_time" content="[^"]*">': f'<meta property="article:published_time" content="{published}">',
        r'<meta property="article:modified_time" content="[^"]*">': f'<meta property="article:modified_time" content="{modified}">',
        r'<meta name="twitter:image" content="[^"]*">': f'<meta name="twitter:image" content="https://carter6713.github.io{cover}">',
        r'<title>.*? - 6\+7</title>': f'<title>{html.escape(title)} - 6+7</title>',
    }
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result, count=1)

    result = re.sub(r'\n\s*<meta property="article:tag" content="[^"]*">', "", result)
    head_tags = "".join(f'\n<meta property="article:tag" content="{html.escape(tag)}">' for tag in tags)
    result = result.replace('<meta name="twitter:card"', f'{head_tags}\n<meta name="twitter:card"', 1)
    result = re.sub(
        r"style=\"background: url\('[^']+'\) no-repeat center center; background-size: cover;\"",
        f"style=\"background: url('{cover}') no-repeat center center; background-size: cover;\"",
        result,
        count=1,
    )
    result = re.sub(r'<span id="subtitle" data-typed-text="[^"]*"></span>', f'<span id="subtitle" data-typed-text="{html.escape(title)}"></span>', result, count=1)
    result = re.sub(
        r'<time datetime="[^"]*" pubdate>\s*.*?\s*</time>',
        f'<time datetime="{date} 08:00" pubdate>\n          {localized_date(date)} 上午\n        </time>',
        result,
        count=1,
        flags=re.S,
    )
    result = re.sub(r'\d+ 字', f'{text_count} 字', result, count=1)
    result = re.sub(r'\d+ 分钟', f'{minutes} 分钟', result, count=1)
    result = re.sub(r'<h1 id="seo-header">.*?</h1>', f'<h1 id="seo-header">{html.escape(title)}</h1>', result, count=1)
    result = re.sub(
        r'(<div class="markdown-body">\s*).*?(\s*</div>\s*<hr/>)',
        lambda match: f'{match.group(1)}{post["body"]}{match.group(2)}',
        result,
        count=1,
        flags=re.S,
    )
    result = result.replace(
        'href="/blog/categories/%E6%8A%80%E6%9C%AF/" class="category-chain-item">技术</a>',
        'href="/blog/categories/" class="category-chain-item">生活</a>',
    )
    result = re.sub(
        r'(<div class="post-meta">\s*<i class="iconfont icon-tags"></i>).*?(\s*</div>)',
        lambda match: f'{match.group(1)}\n{render_tags(tags, "print-no-link")}\n      {match.group(2)}',
        result,
        count=1,
        flags=re.S,
    )
    license_html = (
        '<div class="license-title">\n'
        f'      <div>{html.escape(title)}</div>\n'
        f'      <div>https://carter6713.github.io{url}</div>\n'
        '    </div>'
    )
    result = re.sub(r'<div class="license-title">.*?</div>\s*</div>', license_html, result, count=1, flags=re.S)
    result = re.sub(r'(<div>发布于</div>\s*<div>).*?(</div>)', rf'\g<1>{localized_date(date)}\2', result, count=1, flags=re.S)
    return result


def index_card(post: dict[str, object]) -> str:
    url = post_url(post)
    tags = "\n".join(f'              <a href="/blog/tags/">#{html.escape(tag)}</a>' for tag in list(post["tags"]))
    return f'''  <div class="row mx-auto index-card">
    <div class="col-12 col-md-4 m-auto index-img">
      <a href="{url}" target="_self">
        <img src="{post['cover']}" srcset="/blog/img/loading.gif" lazyload alt="{html.escape(str(post['title']))}">
      </a>
    </div>
    <article class="col-12 col-md-8 mx-auto index-info">
      <h2 class="index-header"><a href="{url}" target="_self">{html.escape(str(post['title']))}</a></h2>
      <a class="index-excerpt" href="{url}" target="_self"><div>{html.escape(str(post['summary']))}</div></a>
      <div class="index-btm post-metas">
        <div class="post-meta mr-3"><i class="iconfont icon-date"></i><time datetime="{post['date']}" pubdate>{post['date']}</time></div>
        <div class="post-meta mr-3 d-flex align-items-center"><i class="iconfont icon-category"></i><span class="category-chains"><span class="category-chain"><a href="/blog/categories/" class="category-chain-item">生活</a></span></span></div>
        <div class="post-meta"><i class="iconfont icon-tags"></i>
{tags}
        </div>
      </div>
    </article>
  </div>'''


def update_index(posts: list[dict[str, object]]) -> None:
    path = BLOG / "index.html"
    page = path.read_text(encoding="utf-8")
    cards = "\n\n".join(index_card(post) for post in posts)
    block = f"{INDEX_START}\n{cards}\n{INDEX_END}"
    if INDEX_START in page:
        page = re.sub(rf'{re.escape(INDEX_START)}.*?{re.escape(INDEX_END)}', block, page, count=1, flags=re.S)
    else:
        needle = '<h1 style="display: none">6+7</h1>'
        page = page.replace(needle, f'{needle}\n\n{block}', 1)
    path.write_text(clean_text(page), encoding="utf-8")


def update_archive(posts: list[dict[str, object]]) -> None:
    path = BLOG / "archives" / "index.html"
    page = path.read_text(encoding="utf-8")
    entries = "\n".join(
        f'''    <a href="{post_url(post)}" class="list-group-item list-group-item-action">
      <time>{str(post['date'])[5:]}</time>
      <div class="list-group-item-title">{html.escape(str(post['title']))}</div>
    </a>''' for post in posts
    )
    block = f"{ARCHIVE_START}\n{entries}\n    {ARCHIVE_END}"
    page = re.sub(r'共计 \d+ 篇文章', f'共计 {len(posts) + 1} 篇文章', page, count=1)
    if ARCHIVE_START in page:
        page = re.sub(rf'{re.escape(ARCHIVE_START)}.*?{re.escape(ARCHIVE_END)}', block, page, count=1, flags=re.S)
    else:
        needle = '<p class="h5">2026</p>'
        page = page.replace(needle, f'{needle}\n      \n    {block}', 1)
    path.write_text(clean_text(page), encoding="utf-8")


def main() -> None:
    posts = sorted((parse_post(path) for path in SOURCE.glob("*.md")), key=lambda post: str(post["date"]), reverse=True)
    template = ARTICLE_TEMPLATE.read_text(encoding="utf-8")
    for post in posts:
        target = BLOG / str(post["date"]).replace("-", "/") / str(post["slug"]) / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(clean_text(render_article(template, post)), encoding="utf-8")
    update_index(posts)
    update_archive(posts)


if __name__ == "__main__":
    main()
