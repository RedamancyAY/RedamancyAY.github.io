import json
import yaml
import re
import os

# 配置需要高亮的名字
HIGHLIGHT_NAMES = [
    "Zhang, Kuiyuan",
    "Kuiyuan Zhang",
    "Zhang Kuiyuan",
    "张魁元"  # 如果有中文名字也可以添加
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
            regex_pattern = r'(?<!\*)\b' + re.escape(pattern) + r'\b(?!\*)'
            highlighted_authors = re.sub(
                regex_pattern, 
                f'**{pattern}**', 
                highlighted_authors, 
                flags=re.IGNORECASE
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

def parse_bibtex_advanced(bib_content):
    """改进的 BibTeX 解析器，专门处理 biblatex 格式"""
    publications = []
    
    # 按条目分割，保持完整的条目结构
    entries = re.split(r'(?=^@\w+\{)', bib_content, flags=re.MULTILINE)
    
    for entry in entries:
        if not entry.strip() or not entry.startswith('@'):
            continue
        
        # 提取条目类型和键
        header_match = re.match(r'^@(\w+)\{([^,\s]+)\s*,', entry, re.MULTILINE)
        if not header_match:
            continue
        
        entry_type, key = header_match.groups()
        
        pub = {
            'key': key.strip(),
            'type': entry_type.lower(),
        }
        
        # 更精确的字段解析 - 处理多行和嵌套大括号
        field_matches = []
        
        # 使用递归下降解析器的简化版本
        lines = entry.split('\n')[1:]  # 跳过第一行（@type{key,）
        
        current_field = None
        current_value = []
        brace_count = 0
        in_field = False
        
        for line in lines:
            line = line.strip()
            if not line or line == '}':
                continue
            
            # 检查是否是新字段的开始
            field_start = re.match(r'^(\w+)\s*=\s*(.*)$', line)
            if field_start and brace_count == 0:
                # 保存之前的字段
                if current_field and current_value:
                    field_matches.append((current_field, ' '.join(current_value)))
                
                # 开始新字段
                current_field = field_start.group(1)
                value_part = field_start.group(2)
                current_value = [value_part]
                
                # 计算大括号
                brace_count = value_part.count('{') - value_part.count('}')
                in_field = True
            elif in_field:
                # 继续当前字段
                current_value.append(line)
                brace_count += line.count('{') - line.count('}')
            
            # 如果大括号平衡，字段结束
            if brace_count == 0 and in_field:
                in_field = False
        
        # 保存最后一个字段
        if current_field and current_value:
            field_matches.append((current_field, ' '.join(current_value)))
        
        # 处理解析出的字段
        for field_name, field_value in field_matches:
            # 清理字段值
            field_value = field_value.strip()
            
            # 移除开头和结尾的大括号以及逗号
            field_value = re.sub(r'^[{,\s]+|[},\s]+$', '', field_value)
            
            # 清理并存储
            cleaned_value = clean_bibtex_field(field_value)
            pub[field_name.lower()] = cleaned_value
        
        # 对所有字段进行最终清理，确保没有遗漏的大括号
        for key in pub:
            if isinstance(pub[key], str):
                pub[key] = clean_bibtex_field(pub[key])
        
        if pub.get('title') or pub.get('booktitle') or pub.get('journaltitle'):
            publications.append(pub)
    
    return publications

def format_apa(pub, gs_data, highlight_names=None):
    """格式化为 APA 引用格式"""
    # 获取引用数量
    citations = 0
    if gs_data and 'publications' in gs_data:
        pub_title = pub.get('title', '').lower()
        for gs_pub in gs_data['publications'].values():
            gs_title = gs_pub.get('bib', {}).get('title', '').lower()
            # 使用部分匹配来找到对应的论文
            if pub_title and gs_title and (
                pub_title in gs_title or gs_title in pub_title or
                any(word in gs_title for word in pub_title.split()[:3] if len(word) > 3)
            ):
                citations = gs_pub.get('num_citations', 0)
                break
    
    # 格式化作者并高亮
    authors = pub.get('author', '').replace(' and ', ', ')
    if highlight_names:
        authors = highlight_authors(authors, highlight_names)
    
    # 格式化年份
    date_str = pub.get('date', pub.get('year', ''))
    year = date_str.split('-')[0] if date_str else ''
    
    # 构建 APA 格式
    apa_parts = []
    
    if authors:
        apa_parts.append(authors)  # 不再额外加粗，因为高亮的名字已经加粗了
    
    if year:
        apa_parts.append(f"({year})")
    
    # 标题 - 再次清理确保没有双大括号
    if pub.get('title'):
        title = clean_bibtex_field(pub.get('title'))
        apa_parts.append(f"*{title}*")
    
    # 会议/期刊名称 - biblatex 使用 booktitle 表示会议
    venue = pub.get('journaltitle', pub.get('booktitle', ''))
    if venue:
        venue = clean_bibtex_field(venue)
        apa_parts.append(f"**{venue}**")
    
    # 添加卷号和页码
    volume_parts = []
    if pub.get('volume'):
        volume_parts.append(f"Vol. {pub.get('volume')}")
    if pub.get('number'):
        volume_parts.append(f"No. {pub.get('number')}")
    if pub.get('pages'):
        pages = pub.get('pages').replace('--', '-')  # 处理 LaTeX 的长破折号
        volume_parts.append(f"pp. {pages}")
    
    if volume_parts:
        apa_parts.append(', '.join(volume_parts))
    
    citation = '. '.join(apa_parts) + '.'
    
    # 添加指标
    metrics = []
    if citations > 0:
        metrics.append(f"📊 被引 {citations} 次")
    if pub.get('jcr') and pub.get('jcr') != 'None':
        metrics.append(f"🏆 JCR {pub.get('jcr')}")
    if pub.get('if'):
        metrics.append(f"📈 IF: {pub.get('if')}")
    if pub.get('ccf') and pub.get('ccf') != 'None':
        metrics.append(f"🎯 CCF {pub.get('ccf')}")
    
    # 添加链接
    links = []
    if pub.get('url'):
        links.append(f"[URL]({pub.get('url')})")
    if pub.get('github'):
        links.append(f"[GitHub]({pub.get('github')})")
    if pub.get('doi'):
        links.append(f"[DOI](https://doi.org/{pub.get('doi')})")
    
    # 组合结果 - 最终清理
    result = {
        'citation': citation,
        'metrics': ' | '.join(metrics) if metrics else '',
        'links': ' '.join(links) if links else '',
        'year': int(year) if year.isdigit() else 0,
        'citations': citations,
        'type': pub.get('type', ''),
        'venue': clean_bibtex_field(venue) if venue else '',
        'title': clean_bibtex_field(pub.get('title', ''))
    }
    
    return result

def main():
    # 检查并读取 BibTeX 文件
    if not os.path.exists('paper.bib'):
        print("错误：找不到 paper.bib 文件")
        return
    
    with open('paper.bib', 'r', encoding='utf-8') as f:
        bib_content = f.read()
    
    # 读取 Google Scholar 数据（可选）
    gs_data = None
    if os.path.exists('gs-data.json'):
        try:
            with open('gs-data.json', 'r', encoding='utf-8') as f:
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
        print("警告：找不到 gs-data.json 文件，将不包含引用数据")
    
    # 解析和格式化
    publications = parse_bibtex_advanced(bib_content)
    print(f"从 BibTeX 文件中解析出 {len(publications)} 篇论文")
    
    # 显示高亮配置
    print(f"\n将高亮以下作者名字: {', '.join(HIGHLIGHT_NAMES)}")
    
    # 调试：显示解析的字段
    for pub in publications:
        print(f"\n解析的论文: {pub.get('key', 'Unknown')}")
        print(f"  标题: {pub.get('title', 'Missing')}")
        print(f"  会议/期刊: {pub.get('booktitle', pub.get('journaltitle', 'Missing'))}")
        print(f"  作者: {pub.get('author', 'Missing')}")
        print(f"  年份: {pub.get('date', pub.get('year', 'Missing'))}")
    
    formatted_pubs = []
    for pub in publications:
        formatted = format_apa(pub, gs_data, HIGHLIGHT_NAMES)
        formatted_pubs.append(formatted)
    
    # 按年份排序
    formatted_pubs.sort(key=lambda x: x['year'], reverse=True)
    
    # 确保 _data 目录存在
    os.makedirs('_data', exist_ok=True)
    
    # 生成 YAML 数据文件
    try:
        with open('_data/publications.yml', 'w', encoding='utf-8') as f:
            yaml.dump(formatted_pubs, f, allow_unicode=True, default_flow_style=False)
        print(f"\n成功生成 _data/publications.yml，包含 {len(formatted_pubs)} 篇论文")
        
        # 显示生成的数据预览
        print("\n生成的论文数据预览:")
        for pub in formatted_pubs[:2]:  # 只显示前两篇
            print(f"- 标题: {pub['title']}")
            print(f"  作者: {pub['citation'].split('.')[0]}")  # 显示作者部分
            print()
            
    except Exception as e:
        print(f"错误：无法写入 YAML 文件: {e}")

if __name__ == "__main__":
    main()