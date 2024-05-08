import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from urllib import parse
import math
from time import sleep
import pandas as pd


class GoogleBibtex(object):
    def __init__(self, driver_path, gg_search_url):
        self.service = None
        self.driver = None
        self.first_author_names = []
        self.gg_search_url = gg_search_url
        self.driver_path = driver_path
        self.reset(driver_path)

    def reset(self, driver_path):
        self.service = Service(driver_path)
        option = webdriver.ChromeOptions()
        # option.add_argument('headless')  # no show window
        self.driver = webdriver.Chrome(service=self.service, options=option)
        self.driver.set_window_size(800, 800)

    def get_author(self, author_name):
        strto_pn = parse.quote(author_name)
        url = self.gg_search_url + "\"" + strto_pn + "\""
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 5).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class="gs_ai_aff"]'))
            )
        except Exception as e:
            print('Error:', e)
            return 'No information found for this author.'
        # 选择第一个
        result = self.driver.find_element(By.CSS_SELECTOR, 'div[class="gs_ai_aff"]')
        return result.text

    def _quit_driver(self, ):
        self.driver.quit()
        self.service.stop()

    @staticmethod
    def results_writer(results, output_file_path):
        df = pd.DataFrame(results, columns=['First Author Name', 'Affiliation'])
        df.to_excel(output_file_path, index=False)

    def run(self, first_author_names, output_file_path, reset_len=80):
        """
        @params:
            first_author_names: [LIST], your paper names.
            reset_len: [INT], for avoid the robot checking,
            you need to reset the driver for more times, default is 10 papers
        """
        self.first_author_names = first_author_names
        paper_len = len(first_author_names)
        rest = paper_len % reset_len
        task_packs = []
        if paper_len > reset_len:
            groups_len = int(math.floor(paper_len / reset_len))  # 21/20 = 1
            for i in range(groups_len):
                sub_names = first_author_names[i * reset_len: (i + 1) * reset_len]
                task_packs.append(sub_names)

        task_packs.append(first_author_names[-1 * rest:])
        results = []
        for ti in task_packs:
            for pn in ti:
                if len(pn) < 3:
                    continue
                print('\n---> Searching author\'s affiliation: {} ---> \n'.format(pn))
                author = self.get_author(pn)
                print(author)
                results.append((pn, author))
            self._quit_driver()
            sleep(3)
            self.reset(self.driver_path)
            print('-' * 10 + '\n Reset for avoiding robot check')
        self.results_writer(results, output_file_path)
        return results


def extract_first_author(bibtex):
    # 使用正则表达式从BibTeX中提取作者信息
    match = re.search(r'author\s*=\s*{([^}]+)}', bibtex, re.IGNORECASE)
    if match:
        # 去除\ ' { } 等字符
        match = re.sub(r'[\\\'{}]', '', match.group(1))
        # 获取第一作者
        authors = match.split(' and ')
        first_author = authors[0].strip()
        return first_author
    return None


if __name__ == '__main__':
    driver_path = "/Users/k/Documents/GitHub/LiteratureProcess/chromedriver"
    input_file_path = "output_ai.xlsx"
    output_file_path = "output2_ai.xlsx"
    data = pd.read_excel(input_file_path)
    first_author_names = []
    for index, row in data.iterrows():
        bibtex_entry = row['BibTeX']
        first_author = extract_first_author(bibtex_entry)
        first_author_names.append(first_author)

    gg_search_url = r'https://scholar.google.com/citations?view_op=search_authors&mauthors='
    ggb = GoogleBibtex(driver_path=driver_path, gg_search_url=gg_search_url)
    results = ggb.run(first_author_names=first_author_names, output_file_path=output_file_path)
