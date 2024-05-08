import bibtexparser


def bibtex_to_text(bibtex_str):
    # 加载并解析BibTeX数据
    bib_database = bibtexparser.loads(bibtex_str)

    references = []
    for entry in bib_database.entries:
        if entry['ENTRYTYPE'] == 'article':
            ref = f"{entry.get('author')}. \"{entry.get('title')}\". {entry.get('journal')}, vol. {entry.get('volume')}, no. {entry.get('number')}, pp. {entry.get('pages')}, {entry.get('year')}."
        elif entry['ENTRYTYPE'] == 'book':
            ref = f"{entry.get('author')}. {entry.get('title')}. {entry.get('publisher')}, {entry.get('year')}."
        elif entry['ENTRYTYPE'] == 'misc':
            # 处理misc类型，特别是包含URL的情况
            url = entry.get('howpublished', '').replace('\\url{', '').replace('}', '')  # 简化处理URL
            ref = f"{entry.get('author')}. \"{entry.get('title')}\". {url}, {entry.get('year')}."
        else:
            ref = None
        if ref:
            references.append(ref)

    return references


# 示例使用
if __name__ == '__main__':
    text = """
        @misc{RDF_W3,
            author = {Jennifer Riggins},
            title = {How Google Unlocks and Measures Developer Productivity},
            year = {2023},
            howpublished = {\\url{https://thenewstack.io/how-google-unlocks-and-measures-developer-productivity/#circle=on}}
        }
    """
    references = bibtex_to_text(text)
    for ref in references:
        print(ref)
