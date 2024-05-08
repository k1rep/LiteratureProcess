import re
import sqlite3

import pandas as pd


def normalize_title(title):
    """标准化标题，移除额外的空格、特定字符，并转换为小写。"""
    processed_title = re.sub(r'[^a-zA-Z]', '', title).lower()
    return processed_title, title


def read_titles_from_excel(file_path, sheet_name):
    """从指定的Excel文件和工作表中读取多列参考文献标题."""
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    # 假设参考文献标题列名格式为 'Reference 1', 'Reference 2', ...
    # 自动找出所有 'Reference' 开头的列
    reference_columns = [col for col in df.columns if col.startswith('Reference')]
    processed_to_original = {}
    titles = set()
    for column in reference_columns:
        for title in df[column].dropna():
            processed_title, original_title = normalize_title(title)
            titles.add(processed_title)
            processed_to_original[processed_title] = original_title
    return titles, processed_to_original


def read_paper_titles_from_excel(file_path, sheet_name, column_name):
    """从指定的Excel文件和工作表中读取论文标题列."""
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    processed_to_original = {}
    titles = set()
    for title in df[column_name].dropna():
        processed_title, original_title = normalize_title(title)
        titles.add(processed_title)
        processed_to_original[processed_title] = original_title  # 映射处理后的标题到原始标题
    return titles, processed_to_original


def read_paper_titles_from_excel_v2(file_path, sheet_name, column_name):
    """从指定的Excel文件和工作表中读取论文标题列."""
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    titles = set()
    for title in df[column_name].dropna():
        processed_title, original_title = normalize_title(title)
        titles.add(processed_title)
    return titles


def read_paper_doi_and_references_from_sqlite(db_path, table_name, columns):
    """从指定的 SQLite 数据库和表中读取论文 DOI 和引用文本."""
    import sqlite3
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
    data = c.fetchall()
    # 建立映射
    doi_ref_map = {}
    for row in data:
        ref = row[1]
        doi = row[0]
        processed_title, original_title = normalize_title(ref)
        doi_ref_map[doi] = processed_title
    return doi_ref_map


def compare_references_with_papers(ref_titles, all_paper_titles, processed_to_original):
    """对比参考文献标题和所有论文标题，查找交集."""
    intersection = ref_titles.intersection(all_paper_titles)
    return {processed_to_original[title] for title in intersection}


def compare_references_with_papers_v2(doi_ref_map, all_paper_titles):
    """对比参考文献标题和所有论文标题，查找交集，并返回所有公共子字符串和doi。"""
    res = dict()
    for doi, ref_title in doi_ref_map.items():
        for paper_title in all_paper_titles:
            if paper_title in ref_title:
                res[paper_title] = doi
    return res


def test():
    # 计算每个单元格含有多少字符
    data = pd.read_excel('ai_references.xlsx')
    data['References'] = data['References'].apply(lambda x: len(x))
    print(data)


def test1(title):
    # 查找数据库中是否真的存在引文标题
    conn = sqlite3.connect('references.db')
    c = conn.cursor()
    c.execute("SELECT reference_text FROM ai_reference")
    data = c.fetchall()
    for row in data:
        process_title, original_title = normalize_title(row[0])
        process_title1, original_title1 = normalize_title(title)
        if process_title1 in process_title:
            print(process_title1)


def join_doi_title(output_path):
    # 将doi和标题连接起来
    data = pd.read_excel(output_path)
    data_title = pd.read_excel('doi_se_0422.xlsx', usecols=['Title', 'DOI'])
    data = pd.merge(data, data_title, on='DOI', how='left')
    data.to_excel(output_path, index=False)


if __name__ == "__main__":
    # 读取数据
    # ref_titles, ref_to_original = read_titles_from_excel('output4_ai.xlsx', 'Sheet1')
    # all_paper_titles, paper_to_original = read_paper_titles_from_excel('papers_all.xlsx', 'se-papers', 'Title')
    #
    # # 对比标题
    # existing_titles = compare_references_with_papers(ref_titles, all_paper_titles, ref_to_original)
    output_path = 'existing_titles_found_se_se.xlsx'
    doi_ref_map = read_paper_doi_and_references_from_sqlite('references.db', 'se_reference', ['doi', 'reference_text'])
    all_paper_titles, to_original_paper = read_paper_titles_from_excel('papers0422.xlsx', 'se', 'Title')
    existing_titles = compare_references_with_papers_v2(doi_ref_map, all_paper_titles)
    # 输出结果
    print("以下文献标题存在于当前论文的所有引用Ref中:")

    for title, doi in existing_titles.items():
        print(doi)
        print(to_original_paper[title])
    # 保存结果到 Excel 文件
    output_df = pd.DataFrame({'DOI': list(existing_titles.values()),
                              'Title': [to_original_paper.get(x, '') for x in existing_titles.keys()]})
    output_df.to_excel(output_path, index=False)
    join_doi_title(output_path)
