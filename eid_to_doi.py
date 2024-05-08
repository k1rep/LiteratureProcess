import re

import pandas as pd
from urllib import parse

from googlesearch import search
from pybliometrics.scopus import AbstractRetrieval, ScopusSearch
from pybliometrics.scopus import config

# 设置 API Key 和 Institution Token
config['Authentication']['APIKey'] = '4b15d76171db4f4d866d1a056d9185f5'
config['Authentication']['InstToken'] = ''


def get_doi_from_scopus(title):
    try:
        # 使用精确的文章标题进行 Scopus 搜索
        search_query = f'TITLE("{title}")'
        search_result = ScopusSearch(search_query, download=True)

        # 获取搜索结果中的第一篇文章的 EID
        eids = search_result.get_eids()
        if eids:
            eid = eids[0]  # 只处理第一篇文章
            # 使用文献的 EID 获取详细信息
            doc = AbstractRetrieval(eid, view='FULL')
            # 返回 DOI
            return doc.doi
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def get_title_from_excel(file_path, sheet_name):
    # 从 Excel 文件读取文章标题
    papers = pd.read_excel(file_path, sheet_name=sheet_name)
    titles = papers['Title'].to_list()
    return titles


def find_doi_via_google(title):
    query = f"{title} DOI"
    for result in search(query, num_results=1):
        doi_pattern = re.compile(r'10.\d{4,9}/[-._;()/:A-Z0-9]+', re.IGNORECASE)
        matches = doi_pattern.findall(str(result))
        return matches[0] if matches else None


if __name__ == '__main__':
    input_file_path = "papers0422.xlsx"
    output_file_path = 'doi_se_0422.xlsx'
    paper_names = get_title_from_excel(input_file_path, sheet_name='se')

    # 保存结果到字典，后续可以输出到 Excel
    results = {}

    for title in paper_names:
        # URL 解码
        title = parse.unquote(title)
        dois = get_doi_from_scopus(title)
        results[title] = dois

    for title, doi in results.items():
        if not doi:
            doi = find_doi_via_google(title)
            results[title] = doi
    # 输出结果到 Excel 文件
    df = pd.DataFrame(results.items(), columns=['Title', 'DOI'])
    df.to_excel(output_file_path, index=False)
