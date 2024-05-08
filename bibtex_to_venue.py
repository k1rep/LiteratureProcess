import pandas as pd


def get_venue_from_bibtex(bibtex):
    # 如果@后是inproceedings，说明是会议论文
    if "@inproceedings" in bibtex:
        if "workshop" in bibtex or "Workshop" in bibtex:
            venue = "Workshop"
            return venue
        venue = "Conference"
        return venue
    # 如果@后是article，说明是期刊论文
    elif "@article" in bibtex:
        venue = "Journal"
        return venue
    else:
        return None


if __name__ == '__main__':
    file_path = 'output.xlsx'
    df = pd.read_excel(file_path)
    for index, row in df.iterrows():
        bibtex = row['BibTeX']
        venue = get_venue_from_bibtex(bibtex)
        df.loc[index, 'Venue'] = venue
    df.to_excel(file_path, index=False)
