import csv
import os
import re

import pandas as pd


def read_bib(filepath, papers):
    # read bib file
    with open(filepath) as bibtex_file:
        bibtex_str = bibtex_file.read()

    # match @xxx{..., ...}
    entries = re.findall(r'@.*?{(?:.*?)\n(.*?)(?=\n@|\n\n)', bibtex_str, re.DOTALL)
    for entry in entries:
        # title = re.search(r'((?<!book)title|标题)\s*=\s*{(.*?)}', entry, re.DOTALL)
        title = re.search(r'(title|标题)\s*=\s*{(.*?)}', entry, re.DOTALL)
        keywords = re.search(r'(keywords|关键词)\s*=\s*{(.*?)}', entry, re.DOTALL)
        abstract = re.search(r'(abstract|摘要)\s*=\s*{(.*?)}', entry, re.DOTALL)
        year = re.search(r'(year|年份)\s*=\s*{(.*?)}', entry, re.DOTALL)
        # numpages = re.search(r'(numpages|页数)\s*=\s*{(.*?)}', entry, re.DOTALL)
        # match 'title' or '标题', 'keywords' or '关键字', and 'abstract' or '摘要'
        title = title.group(2) if title else ''
        keywords = keywords.group(2) if keywords else ''
        abstract = abstract.group(2) if abstract else ''
        year = year.group(2) if year else ''
        # numpages = numpages.group(2) if numpages else 0

        data = [title, keywords, abstract, year]
        papers.append(data)


def save_2_excel(papers, columns, tar_src):
    # save to excel
    df = pd.DataFrame(papers, columns=columns)
    df.to_excel(tar_src, index=False)


def remove_empty_abstract(paper_list):
    temp_papers = []
    for p in paper_list:
        if p[2] is None or p[2] == '':
            print(p)
            continue
        else:
            temp_papers.append(p)
    return temp_papers


def remove_duplicate(paper_list):
    papers_set = set()
    unique_papers = []
    for p in paper_list:
        title = p[0].lower()
        if title not in papers_set:
            unique_papers.append(p)
            papers_set.add(title)
        else:
            print(title)
    return unique_papers


csv_headers = ['文献标题', '摘要', '作者关键字', '起始页码', '结束页码', '年份']

if __name__ == "__main__":
    root_src = "/Users/k/Downloads/"
    file_list = []
    for root, dirs, files in os.walk(root_src):
        for file_name in files:
            file_list.append(os.path.join(root, file_name))

    papers = []
    for fp in file_list:
        if 'bib' in fp:
            read_bib(fp, papers)

    save_2_excel(papers, ['Title', 'Keywords', 'Abstract', 'Year'], root_src+'all.xlsx')

    papers = remove_empty_abstract(papers)
    print(f'{"=" * 10} Duplicated {"=" * 10}')
    papers = remove_duplicate(papers)

    save_2_excel(papers, ['Title', 'Keywords', 'Abstract', 'Year'], root_src+'duplicated.xlsx')
