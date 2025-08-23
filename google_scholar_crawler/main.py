from scholarly import scholarly
import jsonpickle
import json
from datetime import datetime
import os
import bibtexparser
import re

### get full google scholar data


def get_full_gs_data():
    global author

    print("准备获取 author id...", flush=True)
    try:
        print("使用 GOOGLE_SCHOLAR_ID 环境变量中的 ID 进行查询", flush=True)
        
        try:
            id = os.environ["GOOGLE_SCHOLAR_ID"]
        except Exception as e:
            print("警告：未设置 GOOGLE_SCHOLAR_ID 环境变量，使用默认 ID 代替", e, flush=True)
            id = "Cn-lWgIAAAAJ"
        
        print(f"查询 author id: {id}", flush=True)
        
        author = scholarly.search_author_id(id)
        print(f"已获取 author id: {author.get('scholar_id', '未知')}", flush=True)
    except Exception as e:
        print(f"获取 author id 失败: {e}", flush=True)
        raise

    print("准备填充 author 数据...", flush=True)
    try:
        scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])
        print("author 数据填充完成", flush=True)
    except Exception as e:
        print(f"填充 author 数据失败: {e}", flush=True)
        raise

    name = author.get("name", "未知")
    print(f"作者姓名: {name}", flush=True)
    author["updated"] = str(datetime.now())
    author["publications"] = {v["author_pub_id"]: v for v in author.get("publications", [])}
    print("准备写入 author 数据到 results/gs_data.json...", flush=True)
    os.makedirs("results", exist_ok=True)
    with open(f"results/gs_data.json", "w") as outfile:
        json.dump(author, outfile, ensure_ascii=False)
    print("author 数据写入完成", flush=True)


def write_full_citations_data():

    ### citations
    shieldio_data = {
        "schemaVersion": 1,
        "label": "citations",
        "message": f"{author['citedby']}",
    }
    with open(f"results/gs_data_shieldsio.json", "w") as outfile:
        json.dump(shieldio_data, outfile, ensure_ascii=False)


def write_hindex_data():

    ### hindex
    shieldio_data_hindex = {
        "schemaVersion": 1,
        "label": "hindex",
        "message": f"{author['hindex']}",
    }
    with open(f"results/gs_data_shieldsio_hindex.json", "w") as outfile:
        json.dump(shieldio_data_hindex, outfile, ensure_ascii=False)



def clean_bibtex_field(field_value):
    """清理 BibTeX 字段中的特殊字符"""
    if not field_value:
        return field_value
    
    # 递归移除双大括号，直到完全清除
    prev_value = ""
    while prev_value != field_value:
        prev_value = field_value
        # 移除最外层的双大括号
        field_value = re.sub(r'\{\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\}', r'\1', field_value)
        # 移除单层大括号
        field_value = re.sub(r'\{([^{}]+)\}', r'\1', field_value)
    
    # 移除包围整个内容的大括号
    field_value = field_value.strip()
    while field_value.startswith('{') and field_value.endswith('}') and field_value.count('{') == field_value.count('}'):
        field_value = field_value[1:-1].strip()
    
    # 清理多余的空格
    field_value = ' '.join(field_value.split())
    
    return field_value



def parse_bibtex_with_parser(bib_content):
    """使用新版 bibtexparser 解析 BibTeX 文件"""
    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
    bib_database = bibtexparser.loads(bib_content, parser=parser)
    publications = []
    for entry in bib_database.entries:
        pub = {k.lower(): clean_bibtex_field(v) for k, v in entry.items()}
        if pub.get('title') or pub.get('booktitle') or pub.get('journaltitle'):
            publications.append(pub)
    return publications


def normalize_title(title):
    """标准化标题用于匹配"""
    return re.sub(r'\W+', '', title).lower()


def get_paper_citations(pub, gs_data):
    """格式化为 APA 引用格式"""
    # 获取引用数量（优化匹配逻辑）
    citations = 0
    if gs_data and 'publications' in gs_data:
        pub_title_norm = normalize_title(pub.get('title', ''))
        for gs_pub in gs_data['publications'].values():
            gs_title_norm = normalize_title(gs_pub.get('bib', {}).get('title', ''))
            if not pub_title_norm or not gs_title_norm:
                continue
            # 完全匹配
            if pub_title_norm == gs_title_norm:
                citations = gs_pub.get('num_citations', 0)
                break
            # 包含匹配
            if pub_title_norm in gs_title_norm or gs_title_norm in pub_title_norm:
                citations = gs_pub.get('num_citations', 0)
                break
            # 前3个长词交集匹配
            pub_words = set([w for w in pub_title_norm.split() if len(w) > 3][:3])
            gs_words = set([w for w in gs_title_norm.split() if len(w) > 3])
            if pub_words & gs_words:
                citations = gs_pub.get('num_citations', 0)
                break
    return citations
            

def write_paper_citations_data():
    print(os.listdir('../'), flush=True)
    
    
    
    with open('../paper.bib', 'r', encoding='utf-8') as f:
        bib_content = f.read()
    publications = parse_bibtex_with_parser(bib_content)
    
    gs_data = None
    if os.path.exists('results/gs_data.json'):
        try:
            with open('results/gs_data.json', 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    gs_data = json.loads(content)
                else:
                    print("警告：gs-data.json 文件为空")
        except json.JSONDecodeError as e:
            print(f"警告：无法解析 gs-data.json 文件: {e}")
        except Exception as e:
            print(f"警告：读取 gs-data.json 时出错: {e}")
    else:
        print("警告：找不到 gs-data.json 文件，将不包含引用数据", flush=True)
        
        
    for i, pub in enumerate(publications):
        title = pub.get('title', '')
        print(f"{i}/{len(publications)}: Processing paper: {title}", flush=True)
        
        citation_number = get_paper_citations(pub, gs_data)
        pub_title_norm = normalize_title(pub.get('title', ''))
        date_str = pub.get('date', pub.get('year', ''))
        year = date_str.split('-')[0] if date_str else ''
        
        print(f"\t \t Paper: {title}, Year: {year}, Citations: {citation_number}", flush=True)
        
        print("\t \t Writing to results/paper_{year}_{pub_title_norm[:30]}.json", flush=True)
        with open(f"results/paper_{year}_{pub_title_norm[:30]}.json", "w", encoding='utf-8') as outfile:
            shieldio_data = {
                "schemaVersion": 1,
                "label": "citations",
                "message": f"{citation_number}",
            }
            json.dump(shieldio_data, outfile, ensure_ascii=False)
            print("\t \t File written.", flush=True)

    print(os.listdir('results'), flush=True)

if __name__ == "__main__":
    
    try:
        print("Starting Google Scholar data retrieval...", flush=True)
        print("Fetching full Google Scholar data...", flush=True)
        get_full_gs_data()
        print("Writing full citations data...", flush=True)
        write_full_citations_data()
        print("Writing h-index data...", flush=True)
        write_hindex_data()
        print("Writing paper citations data...", flush=True)
        write_paper_citations_data()
    except Exception as e:
        print(f"发生异常: {e}", flush=True)