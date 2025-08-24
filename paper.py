import json
import yaml
import re
import os
import bibtexparser

from google_scholar_crawler.main import parse_bibtex_with_parser, normalize_title, get_paper_citations

# 配置需要高亮的名字
HIGHLIGHT_NAMES = [
    "Zhang, Kuiyuan",
    "Kuiyuan Zhang",
    "Zhang Kuiyuan",
    "张魁元",  # 如果有中文名字也可以添加
]


def highlight_authors(authors, highlight_names=None):
    """高亮指定的作者名字"""
    if not authors or not highlight_names:
        return authors

    highlighted_authors = authors

    for name in highlight_names:
        # 创建不同的匹配模式
        patterns = [
            name,  # 完全匹配
            name.replace(", ", " "),  # 去掉逗号的版本
            name.replace(" ", ", "),  # 添加逗号的版本
        ]

        for pattern in patterns:
            # 使用word boundary确保完整匹配，避免重复高亮
            regex_pattern = r"(?<!\*)\b" + re.escape(pattern) + r"\b(?!\*)"
            highlighted_authors = re.sub(
                regex_pattern,
                f"**{pattern}**",
                highlighted_authors,
                flags=re.IGNORECASE,
            )

    return highlighted_authors


def clean_bibtex_field(field_value):
    """清理 BibTeX 字段中的特殊字符"""
    if not field_value:
        return field_value

    # 递归移除双大括号，直到完全清除
    prev_value = ""
    while prev_value != field_value:
        prev_value = field_value
        # 移除最外层的双大括号
        field_value = re.sub(
            r"\{\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\}", r"\1", field_value
        )
        # 移除单层大括号
        field_value = re.sub(r"\{([^{}]+)\}", r"\1", field_value)

    # 移除包围整个内容的大括号
    field_value = field_value.strip()
    while (
        field_value.startswith("{")
        and field_value.endswith("}")
        and field_value.count("{") == field_value.count("}")
    ):
        field_value = field_value[1:-1].strip()

    # 清理多余的空格
    field_value = " ".join(field_value.split())

    return field_value


# def parse_bibtex_with_parser(bib_content):
#     """使用 bibtexparser 解析 BibTeX 文件（新版API）"""
#     bib_database = bibtexparser.parse_string(bib_content)
#     publications = []
#     for entry in bib_database.entries:
#         pub = {k.lower(): clean_bibtex_field(v) for k, v in entry.items()}
#         if pub.get('title') or pub.get('booktitle') or pub.get('journaltitle'):
#             publications.append(pub)
#     return publications


def format_apa(pub, highlight_names=None):
    """格式化为 APA 引用格式"""
    # 格式化作者并高亮
    authors = pub.get("author", "").replace(" and ", ", ")
    if highlight_names:
        authors = highlight_authors(authors, highlight_names)

    # 格式化年份
    date_str = pub.get("date", pub.get("year", ""))
    year = date_str.split("-")[0] if date_str else ""

    # 构建 APA 格式
    apa_parts = []

    if authors:
        apa_parts.append(authors)  # 不再额外加粗，因为高亮的名字已经加粗了

    if year:
        apa_parts.append(f"({year})")

    # 标题 - 再次清理确保没有双大括号
    if pub.get("title"):
        title = clean_bibtex_field(pub.get("title"))
        apa_parts.append(f"*{title}*")

    # 会议/期刊名称 - biblatex 使用 booktitle 表示会议
    venue = pub.get("journaltitle", pub.get("booktitle", ""))
    if venue:
        venue = clean_bibtex_field(venue)
        apa_parts.append(f"**{venue}**")

    # 添加卷号和页码
    volume_parts = []
    if pub.get("volume"):
        volume_parts.append(f"Vol. {pub.get('volume')}")
    if pub.get("number"):
        volume_parts.append(f"No. {pub.get('number')}")
    if pub.get("pages"):
        pages = pub.get("pages").replace("--", "-")  # 处理 LaTeX 的长破折号
        volume_parts.append(f"pp. {pages}")

    if volume_parts:
        apa_parts.append(", ".join(volume_parts))

    citation = ". ".join(apa_parts) + "."

    # 添加指标
    citations_url = ""
    if pub.get("title") and year:
        pub_title_norm = normalize_title(pub.get("title", ""))[:30]
        citations_url = f"google-scholar-stats/paper_{year}_{pub_title_norm}.json"


    # 添加指标
    metrics = []
    if pub.get("jcr") and pub.get("jcr") != "None":
        metrics.append(
            f'<img src="https://img.shields.io/badge/JCR-{pub["jcr"]}-EDEDED?logo=journal&labelColor=f6f6f6&color=A1C2A&style=flat" alt="JCR分区">'
        )
    if pub.get("zhongkeyuan") and pub.get("zhongkeyuan") != "None":
        metrics.append(
            f'<img src="https://img.shields.io/badge/中科院-{pub["zhongkeyuan"]}-EDEDED?logo=zhongkeyuan&labelColor=f6f6f6&color=A1C2A&style=flat" alt="中科院分区">'
        )
    if pub.get("if"):
        metrics.append(
            f'<img src="https://img.shields.io/badge/IF-{pub["if"]}-EDEDED?logo=impact&labelColor=f6f6f6&color=A1C2A&style=flat" alt="影响因子">'
        )
    if pub.get("ccf") and pub.get("ccf") != "None":
        metrics.append(
            f'<img src="https://img.shields.io/badge/CCF-{pub["ccf"]}-EDEDED?logo=ccf&labelColor=f6f6f6&color=A1C2A&style=flat" alt="CCF分区">'
        )

    # 添加链接
    links = []
    if pub.get("github"):
        links.append(
            f'<a href="{pub["github"]}"><img src="https://img.shields.io/badge/Github-Code-4caf50?logo=github&color=E87355&style=flat" alt="GitHub"></a>'
        )
    if pub.get("doi"):
        links.append(
            f'<a href="https://doi.org/{pub["doi"]}"><img src="https://img.shields.io/badge/DOI-ffffff?logo=doi&style=flat" alt="DOI"></a>'
        )
    elif pub.get("url"):
        links.append(
            f'<a href="{pub["url"]}"><img src="https://img.shields.io/badge/Paper-blue?logo=internet-explorer&style=flat" alt="URL"></a>'
        )

    # 组合结果 - 最终清理
    result = {
        "citation": citation,
        "metrics": " ".join(metrics) if metrics else "",
        "citations_url": citations_url,  # 新增字段
        "links": " ".join(links) if links else "",
        "year": int(year) if year.isdigit() else 0,
        "type": pub.get("type", ""),
        "venue": clean_bibtex_field(venue) if venue else "",
        "title": clean_bibtex_field(pub.get("title", "")),
    }

    return result


def main():
    # 检查并读取 BibTeX 文件
    if not os.path.exists("paper.bib"):
        print("错误：找不到 paper.bib 文件")
        return

    with open("paper.bib", "r", encoding="utf-8") as f:
        bib_content = f.read()


    # 使用 bibtexparser 解析和格式化
    publications = parse_bibtex_with_parser(bib_content)
    print(f"从 BibTeX 文件中解析出 {len(publications)} 篇论文")

    print(f"\n将高亮以下作者名字: {', '.join(HIGHLIGHT_NAMES)}")

    for pub in publications:
        print(f"\n解析的论文: {pub.get('ID', pub.get('key', 'Unknown'))}")
        print(f"  标题: {pub.get('title', 'Missing')}")
        print(
            f"  会议/期刊: {pub.get('booktitle', pub.get('journaltitle', 'Missing'))}"
        )
        print(f"  作者: {pub.get('author', 'Missing')}")
        print(f"  年份: {pub.get('date', pub.get('year', 'Missing'))}")

    formatted_pubs = []
    for pub in publications:
        formatted = format_apa(pub, HIGHLIGHT_NAMES)
        formatted_pubs.append(formatted)

    formatted_pubs.sort(key=lambda x: x["year"], reverse=True)
    os.makedirs("_data", exist_ok=True)

    try:
        with open("_data/publications.yml", "w", encoding="utf-8") as f:
            yaml.dump(formatted_pubs, f, allow_unicode=True, default_flow_style=False)
        print(f"\n成功生成 _data/publications.yml，包含 {len(formatted_pubs)} 篇论文")
        print("\n生成的论文数据预览:")
        for pub in formatted_pubs[:2]:
            print(f"- 标题: {pub['title']}")
            print(f"  作者: {pub['citation'].split('.')[0]}")
            print()
    except Exception as e:
        print(f"错误：无法写入 YAML 文件: {e}")


if __name__ == "__main__":
    main()
