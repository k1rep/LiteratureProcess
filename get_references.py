from urllib import parse
import pandas as pd
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
from pybliometrics.scopus import config
from xploreapi import XPLORE

# 设置 API Key 和 Institution Token
config['Authentication']['APIKey'] = ''
config['Authentication']['InstToken'] = ''


def get_ieee_reference_title(query):
    """使用 IEEE Xplore API 搜索标题并返回第一个结果的标题."""
    api = XPLORE('qs7y75yx52c5eccsw4355ffp')
    api.article_title = query
    data = api.callAPI()
    print(data)
    return 'No title available'


def get_title_from_excel(file_path, sheet_name):
    # 从 Excel 文件读取文章标题
    papers = pd.read_excel(file_path, sheet_name=sheet_name)
    titles = papers['Title'].to_list()
    return titles


def get_references(title):
    # 使用精确的文章标题进行 Scopus 搜索
    search_query = f'TITLE("{title}")'
    search_result = ScopusSearch(search_query, download=True)
    references_list = []

    # 获取搜索结果中的第一篇文章的 EID
    eids = search_result.get_eids()
    if eids:
        eid = eids[0]  # 只处理第一篇文章
        abstract = AbstractRetrieval(eid, view='FULL')
        references = abstract.references
        if references:
            for ref in references:
                if ref is not None and ref.title:
                    references_list.append(ref.title)
                else:
                    # Scopus 没有标题，尝试使用 IEEE Xplore API
                    ieee_title = get_ieee_reference_title(ref.title if ref.title else title)
                    references_list.append(ieee_title)
    return references_list


if __name__ == "__main__":
    input_file_path = "papers_all.xlsx"
    output_file_path = 'output4_ai.xlsx'
    paper_names = get_title_from_excel(input_file_path, sheet_name='ai-papers')

    # 保存结果到字典，后续可以输出到 Excel
    results = {}

    for title in paper_names:
        # URL 解码
        title = parse.unquote(title)
        references_titles = get_references(title)
        results[title] = references_titles

    # 计算最大参考文献数量以确定列数
    max_refs = max(len(refs) for refs in results.values())

    # 创建 DataFrame
    # 使用列表推导和字典推导来构建每一行的数据
    data = {
        title: refs + [''] * (max_refs - len(refs))  # 补充空字符串使每行长度一致
        for title, refs in results.items()
    }
    # 转换成 DataFrame，指定列名
    df = pd.DataFrame.from_dict(data, orient='index', columns=[f'Reference {i + 1}' for i in range(max_refs)])

    # 将 DataFrame 保存到 Excel 文件中
    df.to_excel(output_file_path, index_label='Title')
