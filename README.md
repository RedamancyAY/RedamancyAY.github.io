<h1 align="center">
Personal Academic Homepage
</h1>


This is [Personal Academic Homepage](https://redamancyay.github.io/). Forked from: https://github.com/tangjyan/zh-cn  你需要根据原始git仓库，来设置一下Google scholar id。



## Custom Usage


### Step 1. 添加论文信息

在`paper.bib`中，添加你的论文信息，使用bibLatex格式，其他需要添加的项为：
```
  github = {https://github.com/xxxxxxx},
  JCR = {Q1}, 
  zhongkeyuan = {Q1},
  IF = {99999},
  CCF = {A}
```
其中，
- `GitHub`：是论文的GitHub code链接
- `JCR`：表示所发表期刊的JCR分区
- `zhongkeyuan`：表示所发表期刊的中科院分区
- `IF`：表示所发表期刊的IF分数
- `CCF`：表示所发表期刊/会议的CCF分区

⚠️注意，会议不需要填写JCR、zhongkeyuan、IF。


示例：
```bibtex
@article{paper2021,
  title        = {Vx FJ qjljz},
  author       = {San, Zhang and Si, Li},
  date         = {2021-06-01},
  journaltitle = {Signal Processing},
  shortjournal = {Signal Processing},
  volume       = {1},
  pages        = {107},
  issn         = {01-14},
  doi          = {10.1xxxxxxxxx},
  url          = {https://www.sciencedirect.com/xxxxxxxxxxxxxxx},
  urldate      = {2022-09-12},
  langid       = {english},
  github = {https://github.com/xxxxxxxxxxx},
  JCR = {Q2},
  zhongkeyuan = {Q2},
  IF = {4},
  CCF = {C}
}
```

### Step 2. 获取google scholar数据

现在，需要生成google scholar爬虫文件，从而获得每个论文的引用量。


![alt text](<assets/imgs/CleanShot 2025-08-24 at 12.55.21@2x.png>)

手动运行这个action，它会在自己仓库的`google-scholar-stats`分支生成爬虫数据。
![alt text](<assets/imgs/CleanShot 2025-08-24 at 12.56.33@2x.png>)

注意，这个action是每天运行的，都会写入文件到分支。

### Step 3

注意，你需要在python环境中安装`google_scholar_crawler/requirements.txt`里的包！！！



首先，在终端里cd回仓库目录，然后运行脚本：
```
python paper.py
```
这会遍历`paper.bib`里的论文，生成APA论文格式，设置引用数据url为google-scholar-stats分支下的：`paper_{year}_{pub_title}.json`，设置分区，写入到`_data/publications.yml`中。

然后，谷歌爬虫的action是每天运行的，都会写入文件到分支，这样个人主页里的论文，都可以每天实时更新引用量。




