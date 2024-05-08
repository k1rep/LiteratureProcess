import pandas as pd

def year_process():
    data = pd.read_excel('ai_data_all1.xlsx')

    # 将Year列的空删除，下面的内容上移
    data['Year'].dropna(inplace=True)
    data['Year'] = data['Year'].shift(-1)
    data.to_excel('ai_data_all1.xlsx', index=False)


def bibtex_process():
    data = pd.read_excel('papers_all_updated.xlsx', sheet_name='ai-papers')

    # BibTeX列每一个单元格前加上@
    data['BibTeX'] = '@' + data['BibTex'].astype(str)
    data.to_excel('papers_all_updated.xlsx', index=False, sheet_name='ai-papers')


if __name__ == '__main__':
    # year_process()
    bibtex_process()

