import re
import pandas as pd

if __name__ == "__main__":
    paper_file_path = 'papers0422.xlsx'
    cross_ref_file_path = 'cross_reference.xlsx'
    data = pd.read_excel(paper_file_path, sheet_name=None)
    df = pd.read_excel(cross_ref_file_path, sheet_name=None)
    # 论文标题对应id
    papers = dict()
    for key in data.keys():
        for index, row in data[key].iterrows():
            tmp = re.sub(r'[^\w\s]', '', row['Title'])
            tmp = tmp.lower()
            papers[tmp] = row['New-ID']

    df['ai-cite-se']['AI-ID'] = df['ai-cite-se']['AI-Title'].str.replace(r'[^\w\s]', '', regex=True).str.lower().map(papers)
    df['ai-cite-se']['SE-ID'] = df['ai-cite-se']['SE-Title'].str.replace(r'[^\w\s]', '', regex=True).str.lower().map(papers)
    df['se-cite-ai']['SE-ID'] = df['se-cite-ai']['SE-Title'].str.replace(r'[^\w\s]', '', regex=True).str.lower().map(papers)
    df['se-cite-ai']['AI-ID'] = df['se-cite-ai']['AI-Title'].str.replace(r'[^\w\s]', '', regex=True).str.lower().map(papers)
    df['ai-cite-ai']['Cited-ID'] = df['ai-cite-ai']['Cited'].str.replace(r'[^\w\s]', '', regex=True).str.lower().map(papers)
    df['ai-cite-ai']['Cite-ID'] = df['ai-cite-ai']['Cite'].str.replace(r'[^\w\s]', '', regex=True).str.lower().map(papers)
    df['se-cite-se']['Cited-ID'] = df['se-cite-se']['Cited'].str.replace(r'[^\w\s]', '', regex=True).str.lower().map(papers)
    df['se-cite-se']['Cite-ID'] = df['se-cite-se']['Cite'].str.replace(r'[^\w\s]', '', regex=True).str.lower().map(papers)

    with pd.ExcelWriter('cross_reference_with_id.xlsx') as writer:
        for key in df.keys():
            df[key].to_excel(writer, sheet_name=key, index=False)
