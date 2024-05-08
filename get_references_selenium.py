import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

import sqlite3


def setup_database(which):
    # 连接到SQLite数据库
    # 如果文件不存在，会自动在当前目录创建:
    conn = sqlite3.connect('references.db')
    cursor = conn.cursor()
    if which == 'se':
        # 创建一个表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS se_reference (
                id INTEGER PRIMARY KEY,
                doi TEXT,
                reference_text TEXT
            )
        ''')
    elif which == 'ai':
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_reference (
                id INTEGER PRIMARY KEY,
                doi TEXT,
                reference_text TEXT
            )
        ''')
    conn.commit()
    conn.close()


def store_references_to_database(doi, reference_text, which):
    conn = sqlite3.connect('references.db')
    cursor = conn.cursor()
    if which == 'ai':
        cursor.execute('INSERT INTO ai_reference (doi, reference_text) VALUES (?, ?)', (doi, reference_text))
    elif which == 'se':
        cursor.execute('INSERT INTO se_reference (doi, reference_text) VALUES (?, ?)', (doi, reference_text))
    conn.commit()
    conn.close()


def check_doi_in_database(doi, which):
    conn = sqlite3.connect('references.db')
    cursor = conn.cursor()
    try:
        # 执行查询
        if which == 'ai':
            cursor.execute('SELECT * FROM ai_reference WHERE doi = ?', (doi,))
        elif which == 'se':
            cursor.execute('SELECT * FROM se_reference WHERE doi = ?', (doi,))
        result = cursor.fetchone()

        # 检查结果是否为空
        if result is None:
            return None  # 或者你可以返回一个特定的字符串，比如 'DOI not found'
        else:
            return result[2]  # 返回第一个元素，即DOI字符串
    finally:
        # 确保无论如何都关闭数据库连接
        conn.close()


driver_path = '/Users/k/Documents/GitHub/LiteratureProcess/chromedriver'


def get_references_from_acm(doi):
    driver = webdriver.Chrome(service=Service(driver_path))

    url = f'https://dl.acm.org/doi/{doi}'
    # 打开网页
    driver.get(url)
    references_div = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[data-sectionname="References"]')
        )
    )

    # 在找到 'References' div 元素后，进一步操作
    # 如果参考文献是列表项 <li>，找出所有的 <li>
    references_items = references_div.find_elements(By.TAG_NAME, 'li')

    # 提取所有参考文献的文本
    references_text = [item.text for item in references_items]
    # page_content = WebDriverWait(driver, 10).until(
    #         ec.presence_of_element_located(
    #             (By.ID, 'pb-page-content')
    #         )
    #     )
    # main_content = page_content.find_element(By.CSS_SELECTOR, "div[data-pb-dropzone='main']")
    # content_1 = main_content.find_element(By.CSS_SELECTOR, "div[id='skip-to-main-content']")
    # content_2 = content_1.find_element(By.CSS_SELECTOR, "main[class='content csur loi-page no-margin']")
    # content_3 = content_2.find_element(By.CSS_SELECTOR, "div[class='container']")
    # content_4 = content_3.find_element(By.CSS_SELECTOR, "article")
    # # 寻找第二个class为"row"的<div>
    # content_5 = content_4.find_elements(By.CSS_SELECTOR, "div[class='row']")[1]
    # content_6 = content_5.find_element(By.CSS_SELECTOR, "div[class='col-md-8 col-sm-7 sticko__side-content']")
    # content_7 = content_6.find_element(By.CSS_SELECTOR, "div[class='article__body article__abstractView']")
    # content_8 = content_7.find_element(By.CSS_SELECTOR, "div[data-sectionname='References']")
    # content_9 = content_8.find_element(By.CSS_SELECTOR, "ol[class='rlist references__list references__numeric']")
    # res = content_9.find_elements(By.CSS_SELECTOR, "li")
    driver.quit()
    return references_text


def get_references_from_ieee(url):
    driver = webdriver.Chrome(service=Service(driver_path))
    driver.get(url + 'references')

    # Wait until the references are loaded
    # WebDriverWait(driver, 20).until(
    #     ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class="reference-container"]'))
    # )

    # Continue clicking the "Load More" button as long as it is present and clickable
    while True:
        try:
            load_more_button = WebDriverWait(driver, 20).until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, 'button[class="load-more-button"], button[type="button"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
            load_more_button.click()
            # 等待新引用内容加载
            WebDriverWait(driver, 20).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class="reference-container"]'))
            )
        except:
            break  # Break the loop if no more "Load More" button is found or it is not clickable

    # Collect all references after fully loading the page
    references_divs = driver.find_elements(By.CSS_SELECTOR, 'div[class="reference-container"]')
    references_results = [div.get_attribute('innerHTML') for div in references_divs]

    driver.quit()
    return references_results


def get_references_from_sciencedirect(url):
    driver = webdriver.Chrome(service=Service(driver_path))

    # 打开网页
    driver.get(url)
    try:
        references_div = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, 'div[id="preview-section-references"]')
            )
        )
        references_text = references_div.find_elements(By.TAG_NAME, 'li')
    except Exception as e:
        print(f"Error: {str(e)}")
        references_ol = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, 'ol[class="references"]')
            )
        )
        references_text = references_ol.find_elements(By.TAG_NAME, 'li')
    references = []
    for ref in references_text:
        references.append(ref.text)
    driver.quit()
    return references


def get_references_from_springer(url):
    driver = webdriver.Chrome(service=Service(driver_path))

    # 打开网页
    driver.get(url)
    references_div = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[data-container-section="references"]')
        )
    )
    references_text = references_div.find_elements(By.TAG_NAME, 'p')
    references = []
    for ref in references_text:
        references.append(ref.text)
    driver.quit()
    return references


def get_references_from_mdpi(url):
    driver = webdriver.Chrome(service=Service(driver_path))

    # 打开网页
    driver.get(url)
    references_div = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[class="html-back"]')
        )
    )
    references_list = references_div.find_element(By.TAG_NAME, 'ol')
    references_text = references_list.find_elements(By.TAG_NAME, 'li')
    references = []
    for ref in references_text:
        references.append(ref.text)
    driver.quit()
    return references


def get_references_from_tandfonline(url):
    driver = webdriver.Chrome(service=Service(driver_path))

    # 打开网页
    driver.get(url)
    references_div = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located(
            (By.CSS_SELECTOR, 'ul[class="references numeric-ordered-list"]')
        )
    )
    references_text = references_div.find_elements(By.TAG_NAME, 'li')
    references = []
    for ref in references_text:
        references.append(ref.text)
    driver.quit()
    return references


def get_references_from_hindawi(url):
    driver = webdriver.Chrome(service=Service(driver_path))

    # 打开网页
    driver.get(url)
    references_items = WebDriverWait(driver, 10).until(
        ec.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'p[class="referenceText"]')
        )
    )
    references = []
    for ref in references_items:
        references.append(ref.text)
    driver.quit()
    return references


def get_references_from_oaepublish(url):
    driver = webdriver.Chrome(service=Service(driver_path))

    # 打开网页
    driver.get(url)
    references_div = WebDriverWait(driver, 10).until(
        ec.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div[class="references_item"]')
        )
    )
    references = []
    for ref in references_div:
        references_text = ref.find_element(By.TAG_NAME, 'p').text
        references.append(references_text)
    driver.quit()
    return references


def get_references_from_wiley(url):
    driver = webdriver.Chrome(service=Service(driver_path))

    # 打开网页
    driver.get(url)
    references_div = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[aria-labelledby="references-section-1"]')
        )
    )
    references_item = references_div.find_element(By.TAG_NAME, 'ul')
    references_text = references_item.find_elements(By.TAG_NAME, 'li')
    references = []
    for ref in references_text:
        references.append(ref.text)
    driver.quit()
    return references


def get_references_from_frontiersin(url):
    driver = webdriver.Chrome(service=Service(driver_path))

    # 打开网页
    driver.get(url)
    references_div = WebDriverWait(driver, 10).until(
        ec.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div[class="References"]')))
    references = []
    for ref in references_div:
        references_text = ref.find_element(By.TAG_NAME, 'p').text
        references.append(references_text)
    driver.quit()
    return references


def get_references_from_iaesonline(url):
    driver = webdriver.Chrome(service=Service(driver_path))

    # 打开网页
    driver.get(url)
    references_div = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[id="articleCitations"]')
        )
    )
    references_text = references_div.find_elements(By.TAG_NAME, 'p')
    references = []
    for ref in references_text:
        references.append(ref.text)
    driver.quit()
    return references


if __name__ == "__main__":
    setup_database(which='se')
    data = pd.read_excel('doi_se_0422.xlsx')
    # 先向doi.org发起requests请求
    for index, row in data.iterrows():
        # if row['References'] != 'No references available':
        #     continue
        # 如果doi存在于数据库中，跳过
        # if row['DOI'] == check_doi_in_database(str(row['DOI']), which='se'):
        #     continue
        # if check_doi_in_database(str(row['DOI']), which='se') != "No references available":
        #     continue
        try:
            r = requests.get('https://doi.org/' + str(row['DOI']), timeout=10)
            # print(r.url)
            # 检查当前的地址
            if r.url.startswith('https://dl.acm.org/doi/'):
                references = get_references_from_acm(str(row['DOI']))
                print(references)
                store_references_to_database(str(row['DOI']), str(references), which='se')
            elif r.url.startswith('https://ieeexplore.ieee.org/document/'):
                references = get_references_from_ieee(r.url)
                print(references)
                store_references_to_database(str(row['DOI']), str(references), which='se')
            elif r.url.startswith('https://linkinghub.elsevier.com'):
                # 会先跳转到linkinghub.elsevier.com
                references = get_references_from_sciencedirect(r.url)
                print(references)
                store_references_to_database(str(row['DOI']), str(references), which='se')
            elif r.url.startswith('https://link.springer.com'):
                references = get_references_from_springer(r.url)
                print(references)
                store_references_to_database(str(row['DOI']), str(references), which='se')
            elif r.url.startswith('https://www.mdpi.com/'):
                references = get_references_from_mdpi(r.url)
                print(references)
                store_references_to_database(str(row['DOI']), str(references), which='se')
            elif r.url.startswith('https://www.hindawi.com/'):
                references = get_references_from_hindawi(r.url)
                print(references)
                store_references_to_database(str(row['DOI']), str(references), which='se')
            elif r.url.startswith('https://www.tandfonline.com/'):
                references = get_references_from_tandfonline(r.url)
                print(references)
                store_references_to_database(str(row['DOI']), str(references), which='se')
            elif r.url.startswith('https://www.oaepublish.com/'):
                references = get_references_from_oaepublish(r.url)
                print(references)
                store_references_to_database(str(row['DOI']), str(references), which='se')
            elif r.url.startswith('https://onlinelibrary.wiley.com/'):
                references = get_references_from_wiley(r.url)
                print(references)
                store_references_to_database(str(row['DOI']), str(references), which='se')
            elif r.url.startswith('https://www.frontiersin.org/'):
                references = get_references_from_frontiersin(r.url)
                print(references)
                store_references_to_database(str(row['DOI']), str(references), which='se')
            elif r.url.startswith('http://section.iaesonline.com/'):
                # http请求
                references = get_references_from_iaesonline(r.url)
                print(references)
                store_references_to_database(str(row['DOI']), str(references), which='se')
            else:
                store_references_to_database(str(row['DOI']), 'No references available', which='se')
        except Exception as e:
            print(f"Error: {str(e)}")
            store_references_to_database(str(row['DOI']), 'No references available', which='se')
            continue
    # data.to_excel('ai_references.xlsx', index=False)
