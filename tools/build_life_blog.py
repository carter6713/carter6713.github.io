"""Build the lifestyle section as dependency-light static HTML."""

from __future__ import annotations

import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "blog-src" / "life"
BLOG = ROOT / "blog"

LEGACY_POSTS = [
    {
        "title": "我的个人主页搭建记录",
        "date": "2026-08-11",
        "url": "/blog/2026/08/11/%E6%88%91%E7%9A%84%E4%B8%AA%E4%BA%BA%E4%B8%BB%E9%A1%B5%E6%90%AD%E5%BB%BA%E8%AE%B0%E5%BD%95/",
        "cover": "/blog/img/blog-index.jpg",
        "cover_alt": "个人主页搭建记录封面",
        "category": "建站随笔",
        "summary": "从零搭建个人主页与博客的过程记录：在技术实现之外，也重新思考公开表达与长期积累。",
        "tags": ["个人主页", "建站"],
        "legacy": True,
    }
]


def parse_post(path: Path):
    raw = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not match:
        raise ValueError(f"Missing front matter: {path}")
    meta = {}
    for line in match.group(1).splitlines():
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    meta["tags"] = [tag.strip() for tag in meta.get("tags", "").split(",") if tag.strip()]
    meta["body"] = markdown.markdown(
        match.group(2),
        extensions=["extra", "sane_lists"],
        output_format="html5",
    )
    return meta


def nav():
    return """
    <nav class="site-nav" aria-label="主导航">
      <a class="site-mark" href="/blog/">6+7 / LIFE NOTES</a>
      <div class="nav-links">
        <a href="/blog/">文章</a>
        <a href="/blog/archives/">归档</a>
        <a href="/blog/about/">关于我</a>
        <a href="/">主页</a>
      </div>
    </nav>"""


def page(title, description, content, canonical):
    escaped_title = html.escape(title)
    escaped_desc = html.escape(description)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escaped_desc}">
  <meta property="og:title" content="{escaped_title}">
  <meta property="og:description" content="{escaped_desc}">
  <meta property="og:url" content="{canonical}">
  <title>{escaped_title} - 6+7</title>
  <link rel="icon" type="image/svg+xml" href="/images/cowface.svg">
  <link rel="stylesheet" href="/blog/css/editorial.css">
</head>
<body>
{nav()}
{content}
<footer class="site-footer">但行好事，莫问前程 · © 2026 6+7</footer>
</body>
</html>
"""


def post_url(post):
    return post.get("url") or f"/blog/{post['date'].replace('-', '/')}/{post['slug']}/"


def render_article(post):
    url = post_url(post)
    tags = " · ".join(post["tags"])
    content = f"""
    <main class="article-shell">
      <header class="article-head">
        <div class="article-meta">{post['date']} · {html.escape(post['category'])} · {html.escape(tags)}</div>
        <h1>{html.escape(post['title'])}</h1>
        <p class="article-deck">{html.escape(post['summary'])}</p>
      </header>
      <img class="lead-image" src="{post['cover']}" alt="{html.escape(post['cover_alt'])}">
      <article class="article-body">{post['body']}</article>
      <div class="article-footer">作者：6+7 · 本文记录可公开的生活片段，照片中的地点与人物信息均按隐私边界处理。</div>
    </main>"""
    return page(post["title"], post["summary"], content, f"https://carter6713.github.io{url}")


def render_index(posts):
    cards = []
    for post in posts:
        url = post_url(post)
        cards.append(f"""
        <article class="post-card">
          <a href="{url}"><img src="{post['cover']}" alt="{html.escape(post['cover_alt'])}"></a>
          <div class="card-copy">
            <div class="card-meta">{post['date']} · {html.escape(post['category'])}</div>
            <h2><a href="{url}">{html.escape(post['title'])}</a></h2>
            <p>{html.escape(post['summary'])}</p>
            <a class="read-more" href="{url}">继续阅读 →</a>
          </div>
        </article>""")
    content = f"""
    <header class="hero">
      <div>
        <div class="eyebrow">Life notes by 6+7</div>
        <h1>在研究之外，认真生活。</h1>
        <p>这里不追赶热点，只保存那些值得慢一点看的片刻：器物、光线、散步，以及为什么要把生活写下来。</p>
      </div>
      <div class="hero-note">技术与科研笔记放在博客园；这里留给生活。两种记录共同构成一个更完整、也更真实的我。</div>
    </header>
    <main class="post-grid">{''.join(cards)}</main>"""
    return page("生活随笔", "6+7 的个人生活博客", content, "https://carter6713.github.io/blog/")


def render_archive(posts):
    items = "".join(
        f'<li><time>{post["date"]}</time><a href="{post_url(post)}">{html.escape(post["title"])}</a></li>'
        for post in posts
    )
    content = f'<main class="archive"><div class="eyebrow">Archive</div><h1>文章归档</h1><ul class="archive-list">{items}</ul></main>'
    return page("文章归档", "生活随笔文章归档", content, "https://carter6713.github.io/blog/archives/")


def main():
    authored_posts = list(parse_post(p) for p in SOURCE.glob("*.md"))
    posts = sorted(authored_posts + LEGACY_POSTS, key=lambda x: x["date"], reverse=True)
    for post in authored_posts:
        target = BLOG / post["date"].replace("-", "/") / post["slug"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_article(post), encoding="utf-8")
    (BLOG / "index.html").write_text(render_index(posts), encoding="utf-8")
    archive = BLOG / "archives" / "index.html"
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_text(render_archive(posts), encoding="utf-8")


if __name__ == "__main__":
    main()
