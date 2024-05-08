from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd


def read_excel_keyword(keywords):
    xls = pd.read_excel('cross_reference.xlsx', sheet_name=None)
    for sheet_name, df in xls.items():
        keywords_columns = [col for col in df.columns if col.startswith('Keyword')]
        for col in keywords_columns:
            keywords.extend(df[col].to_list())
    return keywords


def get_topk_word_freqs(keywords, word_freq_top_k, topk):
    # font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
    # 创建词云对象
    num = 0
    for keyword in keywords:
        if pd.isna(keyword):
            continue
        if not isinstance(keyword, str):
            keyword = str(keyword)
        # 换行符替换成分号
        keyword = keyword.replace('\n', ';')
        # 使用分号分割文本
        words = keyword.split(';')
        # .apply(lambda x: x.title() if x.islower() else x).to_list()
        words = [word.title() if not word.isupper() else word for word in words]
        # 计算每个词汇的频率
        word_freq = {word: words.count(word) for word in set(words)}
        # 更新词频top-k个
        temp = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        word_freq = dict(temp[:topk])
        word_freq_top_k.update(word_freq)
        # 创建词云对象，使用频率生成词云
        wordcloud = WordCloud(width=3200, height=1600,
                              background_color='white', max_words=200,
                              colormap='viridis').generate_from_frequencies(word_freq)
        num += 1
        # 显示词云图像
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')  # 不显示坐标轴
        plt.show()
        # pdf
        wordcloud.to_file(f'wordcloud{num}_all_authors.pdf')
    return word_freq_top_k


if __name__ == '__main__':
    keywords = []
    word_freq = {}
    keywords = read_excel_keyword(keywords)
    # top-k个词
    top_k = 10
    word_freq_top_k = get_topk_word_freqs(keywords, word_freq, top_k)
    print(word_freq_top_k)
    wordcloud_k = WordCloud(width=3200, height=1600,
                            background_color='white', max_words=200,
                            colormap='viridis').generate_from_frequencies(word_freq_top_k)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud_k, interpolation='bilinear')
    plt.axis('off')
    plt.show()
    # pdf
    wordcloud_k.to_file(f'wordcloud_top_{top_k}_all_authors.pdf')
