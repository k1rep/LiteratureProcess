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
        self.paper_names = []
        self.gg_search_url = gg_search_url
        self.driver_path = driver_path
        self.reset(driver_path)

    def reset(self, driver_path):
        self.service = Service(driver_path)
        option = webdriver.ChromeOptions()
        # option.add_argument('headless')  # no show window
        self.driver = webdriver.Chrome(service=self.service, options=option)
        self.driver.set_window_size(800, 800)

    def get_bib_text(self, paper_title, expected_author=None, expected_year=None):
        strto_pn = parse.quote(paper_title)
        url = self.gg_search_url + "\"" + strto_pn + "\""
        self.driver.get(url)

        # 等待搜索结果加载
        search_results = WebDriverWait(self.driver, 30).until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.gs_ri'))  # 假设每个搜索结果都在一个带有 'gs_ri' 类的div中
        )

        for result in search_results:
            result_text = result.text.lower()
            if expected_author and expected_author.lower() not in result_text:
                continue
            if expected_year and str(expected_year) not in result_text:
                continue

            # 尝试点击引用按钮
            try:
                quote_btn_xpath = "//div[@id='gs_bdy_ccl']//a[.//span[text()='引用']]"
                quote_btn = WebDriverWait(self.driver, 30).until(
                    ec.element_to_be_clickable((By.XPATH, quote_btn_xpath)))
                quote_btn.click()
                bibtex_btn = WebDriverWait(self.driver, 30).until(
                    ec.presence_of_element_located((By.XPATH, '//a[contains(text(), "BibTeX")]'))
                )
                bibtex_btn.click()

                bib_text = WebDriverWait(self.driver, 30).until(
                    ec.presence_of_element_located((By.TAG_NAME, 'pre'))
                )
                print(bib_text.text)
                return bib_text.text
            except Exception as e:
                print(f"Error processing result for {paper_title}: {str(e)}")
                continue
        return None

    def _quit_driver(self, ):
        self.driver.quit()
        self.service.stop()

    @staticmethod
    def results_writer(results, output_file_path='output.xlsx'):
        # write results to excel
        df = pd.DataFrame(results.items(), columns=['Title', 'BibTeX'])
        df.to_excel(output_file_path, index=False)

    def run(self, paper_names, output_file_path, reset_len=10):
        """
        @params:
            paper_names: [LIST], your paper names.
            reset_len: [INT], for avoid the robot checking,
            you need to reset the driver for more times, default is 10 papers
        """
        self.paper_names = paper_names
        paper_len = len(paper_names)
        rest = paper_len % reset_len
        task_packs = []
        if paper_len > reset_len:
            groups_len = int(math.floor(paper_len / reset_len))  # 21/20 = 1
            for i in range(groups_len):
                sub_names = paper_names[i * reset_len: (i + 1) * reset_len]
                task_packs.append(sub_names)

        task_packs.append(paper_names[-1 * rest:])
        results = {}
        for ti in task_packs:
            for pn in ti:
                if len(pn) < 3:
                    continue
                print('\n---> Searching paper: {} ---> \n'.format(pn))
                bibtex = self.get_bib_text(pn)
                print(bibtex)
                results[pn] = bibtex
            self._quit_driver()
            sleep(3)
            self.reset(self.driver_path)
            print('-' * 10 + '\n Reset for avoiding robot check')
        self.results_writer(results, output_file_path)
        return results


def get_title_from_excel(file_path):
    # papers sheet
    papers = pd.read_excel(file_path, sheet_name='se-papers')
    titles = papers['Title'].to_list()
    return titles


if __name__ == "__main__":
    driver_path = '/Users/k/Documents/GitHub/LiteratureProcess/chromedriver'
    input_file_path = "papers_all.xlsx"
    output_file_path = 'output.xlsx'

    gg_search_url = r'https://scholar.google.com.hk/scholar?hl=zh-CN&as_sdt=0%2C5&q='
    ggb = GoogleBibtex(driver_path=driver_path, gg_search_url=gg_search_url)
    paper_names = get_title_from_excel(input_file_path)
    results = ggb.run(paper_names=paper_names, output_file_path=output_file_path)
