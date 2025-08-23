---
permalink: /
title: ""
excerpt: ""
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

{% if site.google_scholar_stats_use_cdn %}
{% assign gsDataBaseUrl = "https://cdn.jsdelivr.net/gh/" | append: site.repository | append: "@" %}
{% else %}
{% assign gsDataBaseUrl = "https://raw.githubusercontent.com/" | append: site.repository | append: "/" %}
{% endif %}
{% assign url_citations = gsDataBaseUrl | append: "google-scholar-stats/gs_data_shieldsio.json" %}
{% assign url_hindex = gsDataBaseUrl | append: "google-scholar-stats/gs_data_shieldsio_hindex.json" %}


<span class='anchor' id='about-me'></span>

我将博士毕业于广东深圳的 哈尔滨工业大学 计算机科学与技术学院，我的导师是[花忠云教授](https://huazhongyun.github.io/)。本科毕业于西安的 西北大学 计算机科学与技术学院。 <a href='https://scholar.google.com/citations?user=Cn-lWgIAAAAJ'><img src="https://img.shields.io/endpoint?url={{ url_citations | url_encode }}&logo=Google%20Scholar&labelColor=f6f6f6&color=9cf&style=flat&label=citations"></a>
<a href='https://scholar.google.com/citations?user=Cn-lWgIAAAAJ'><img src="https://img.shields.io/endpoint?url={{ url_hindex | url_encode }}&logo=Google%20Scholar&labelColor=f6f6f6&color=9cf&style=flat&label=H-index"></a>。


我的研究领域包括：
- 压缩感知
- 图像加密
- 多模态deepfake检测
  

<span class='anchor' id='-xl'></span>

# 🎓 学历
- *2022.03 - Now*, <a href="https://www.hitsz.edu.cn/index.html"><img class="svg" src="https://cdn.jsdelivr.net/gh/RedamancyAY/CloudImage@main/img/202310182132949.png" width="23pt"></a> 哈尔滨工业大学（深圳） 计算机科学与技术学院, 广东深圳, 攻读博士 
- *2019.09 - 2022.01*, <a href="https://www.hitsz.edu.cn/index.html"><img class="svg" src="https://cdn.jsdelivr.net/gh/RedamancyAY/CloudImage@main/img/202310182132949.png" width="23pt"></a> 哈尔滨工业大学（深圳） 计算机科学与技术学院, 广东深圳, 硕士 
- *2015.09 - 2019.06*, <a href="https://www.scu.edu.cn/"><img class="svg" src="https://cdn.jsdelivr.net/gh/RedamancyAY/CloudImage@main/img/202310182134883.png" width="20pt"></a> 西北大学 计算机科学与技术学院, 陕西西安, 本科

<span class='anchor' id='-lwzl'></span>



<span class='anchor' id='-lwzl'></span>
# 📝 论文专利

<!-- {% for pub in site.data.publications %}
- <span class="citation">{{ pub.citation }}</span>{% if pub.metrics %} <span class="metrics">{{ pub.metrics }}</span>{% endif %}{% if pub.links %} <span class="links">{{ pub.links }}</span>{% endif %}
{% endfor %} -->


{% for pub in site.data.publications %}
- <span class="citation">{{ pub.citation }}</span>{% if pub.citations_url %}<span class="metrics"><img src="https://img.shields.io/endpoint?url={{ gsDataBaseUrl | append: pub.citations_url | url_encode }}&logo=Google%20Scholar&labelColor=f6f6f6&color=9cf&style=flat&label=citations" alt="被引次数"></span>{% endif %}{% if pub.metrics %}<span class="metrics">{{ pub.metrics }}</span>{% endif %}{% if pub.links %}<span class="links">{{ pub.links }}</span>{% endif %}
{% endfor %}

<span class='anchor' id='-ryjx'></span>

# 🏅 荣誉奖项
- *2019.11* 获得 CCF

<span class='anchor' id='-xshy'></span>

# 🏛️ 学术会议

<span class='anchor' id='-gzsx'></span>

# 💻 工作实习
- *2023.4 - 2023.11*, 阿里巴巴, 浙江杭州