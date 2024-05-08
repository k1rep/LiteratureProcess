import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# 设置 Chrome 的启动选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式

driver_path = '/Users/k/Documents/GitHub/LiteratureProcess/chromedriver'

# 指定 ChromeDriver 的路径
driver = webdriver.Chrome(options=chrome_options)


def fetch_articles(author):
    # 构造查询 URL
    url = f'https://scholar.google.com/citations?view_op=search_authors&mauthors="{author}"'
    driver.get(url)

    try:
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "div.gsc_sa_ccl"))
        )

        # 点击第一个作者
        author_link = driver.find_element(By.CSS_SELECTOR, "h3.gs_ai_name a")
        author_link.click()
    finally:
        driver.quit()


def read_authors_from_excel(file_path, sheet_name, column_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    authors = df[column_name].dropna().to_list()
    return authors


if __name__ == '__main__':
    authors = read_authors_from_excel('cross_reference.xlsx', sheet_name='ai-cite-se', column_name='First Author')
    for author in authors:
        print("Author:", author)
        for title, abstract in fetch_articles(author):
            print("Title:", title)
            print("Abstract:", abstract)
            print()
        print()
        print()
