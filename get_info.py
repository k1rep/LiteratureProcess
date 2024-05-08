from scholarly import scholarly
import pandas as pd


def fetch_paper_info(title):
    try:
        # 搜索论文标题
        search_query = scholarly.search_pubs(title)
        paper = next(search_query, None)
        print(type(paper))
        if paper:
            # 获取BibTeX
            bibtex = scholarly.bibtex(paper)

            # 尝试获取年份和发表渠道
            year = paper.get('bib', {}).get('year')
            venue = paper.get('journal') or paper.get('bib', {}).get('conference')

            # 尝试获取第一作者的单位国家（不保证总能获取到）
            first_author = paper.get('bib', {}).get('author')[0] if 'author' in paper.get('bib', {}) and paper.get('bib', {}).get('author') else None
            country = "Not available"  # Google Scholar不直接提供机构国家信息

            return {
                'title': paper.get('bib', {}).get('title'),
                'bibtex': bibtex,
                'year': year,
                'venue': venue,
                'first_author_country': country
            }
        else:
            print("No information found for this title.")
            return None
    except Exception as e:
        print("Error occurred while fetching paper info:", e)
        return None


def get_title_from_excel(file_path):
    # papers sheet
    papers = pd.read_excel(file_path, sheet_name='papers')
    titles = papers['Title'].to_list()
    return titles


def update_info_to_excel(file_path, paper_info):
    # papers sheet
    papers = pd.read_excel(file_path, sheet_name='papers')
    papers['Year'] = None
    papers['Venue'] = None
    papers['First Author Country'] = None
    papers['BibTeX'] = None

    for index, row in papers.iterrows():
        title = row['Title']
        info = paper_info.get(title)
        if info:
            papers.loc[index, 'Year'] = info.get('year')
            papers.loc[index, 'Venue'] = info.get('venue')
            papers.loc[index, 'First Author Country'] = info.get('first_author_country')
            papers.loc[index, 'BibTeX'] = info.get('bibtex')

    papers.to_excel(file_path, index=False)


if __name__ == '__main__':
    file_path = 'ai_data_all.xlsx'
    titles = get_title_from_excel(file_path)
    paper_infos = {}
    for title in titles:
        paper_info = fetch_paper_info(title)
        if paper_info:
            paper_infos[title] = paper_info
        print("Title:", title)
        print("Paper Info:", paper_info)
    update_info_to_excel(file_path, paper_infos)
