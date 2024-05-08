from scholarly import ProxyGenerator, scholarly
import pandas as pd

pg = ProxyGenerator()
pg.FreeProxies()


def fetch_paper_bibtex(title):
    try:
        scholarly.use_proxy(pg)
        # 搜索论文标题
        search_query = scholarly.search_pubs(title)
        paper = next(search_query, None)
        print(type(paper))
        if paper:
            # 获取BibTeX
            bibtex = scholarly.bib(paper)
            return bibtex
        else:
            print("No information found for this title.")
            return None
    except Exception as e:
        print("Error occurred while fetching paper info:", e)
        return None


def get_title_from_excel(file_path):
    # papers sheet
    papers = pd.read_excel(file_path)
    titles = papers['Title'].to_list()
    return titles


def update_info_to_excel(file_path, paper_info):
    # papers sheet
    papers = pd.read_excel(file_path)
    papers['BibTeX'] = None

    for index, row in papers.iterrows():
        title = row['Title']
        info = paper_info.get(title)
        if info:
            papers.loc[index, 'BibTeX'] = info.get('bibtex')

    papers.to_excel(file_path, index=False)


if __name__ == '__main__':
    file_path = 'ai_paper.xlsx'
    titles = get_title_from_excel(file_path)
    paper_infos = {}
    for title in titles:
        paper_info = fetch_paper_bibtex(title)
        if paper_info:
            paper_infos[title] = paper_info
        print("Title:", title)
        print("Paper Info:", paper_info)
    update_info_to_excel(file_path, paper_infos)
