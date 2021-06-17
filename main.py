from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

IOS_VERSIONS = {'ISR1905': '282977117', 'ISR1906C': '283035751', 'ISR1921': '282977114', 'ISR1941': '282774238',
                'ISR1941W': '282774241', 'ISR2901': '282774223', 'ISR2911': '282774227', 'ISR2921': '282774229',
                'ISR2951': '282774230', 'ISR3925': '282774222', 'ISR3945': '282774228', 'ISR3925E': '282896995',
                'ISR3945E': '282907259'}
IOSXE_VERSIONS = {'ISR4221': '286310700', 'ISR4321': '286006221', 'ISR4331': '285018115',
                  'ISR4351': '285018114', 'ISR4431': '284358776', 'ISR4451-X': '284389362', 'ISR4461': '286320564',
                  'ASR1001-RP1': '282993672', 'ASR1002-RP1': '282046548', 'ASR1004-RP1': '282046548',
                  'ASR1006-RP1': '282046548', 'ASR1001-HX': '286288843', 'ASR1002-HX': '286288594',
                  'ASR1001-X': '284932298', 'ASR1002-X': '284146581', 'ASR1004-RP2': '282450665',
                  'ASR1006-RP2': '282450665', 'ASR1006-X-RP2': '282450665', 'ASR1009-X-RP2': '282450665',
                  'ASR1012-RP2': '282450665', 'ASR1006-X-RP3': '286308009', 'ASR1009-X-RP3': '286308009',
                  'ASR1012-RP3': '286308009'}


class WebPage:
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('log-level=3')
        self.driver = webdriver.Chrome("chromedriver.exe", options=self.options)

        self.IOS = '280805680'
        self.IOS_XE = '282046477'
        self.plat_type = ''
        self.plat = ''
        self.platform = ''
        self.outputs1 = {}
        self.outputs2 = {}
        self.suggested_versions = []
        self.ios_url = ''

    def get_platform(self):
        # Choose platform and check if it is valid.
        self.platform = input('Please input device(example: ASR1001-RP1, ISR4431, ISR2911): ').upper()
        while True:
            if self.platform in IOS_VERSIONS:
                self.plat = 'IOS'
                self.plat_type = IOS_VERSIONS.get(self.platform)
                break
            elif self.platform in IOSXE_VERSIONS:
                self.plat = 'IOS-XE'
                self.plat_type = IOSXE_VERSIONS.get(self.platform)
                break
            print(f'{self.platform} is not a valid device.')
            self.platform = input('Please input device(example: ASR1001-RP1, ISR4431, ISR2911): ').upper()

    def get_suggested(self):
        if self.plat == 'IOS':
            self.ios_url = f'https://software.cisco.com/download/home/{self.plat_type}/type/{self.IOS}/release/'
        elif self.plat == 'IOS-XE':
            self.ios_url = f'https://software.cisco.com/download/home/{self.plat_type}/type/{self.IOS_XE}/release/'

        # Open url to the chosen device.
        self.driver.get(self.ios_url)

        # Get suggested versions names.
        time.sleep(1)
        suggested = self.driver.find_element_by_xpath('//app-root/div/main/div/div/app-release-page/div/div[1]/'
                                                      'app-release-details/nav/div[4]/tree-root/tree-viewport/div/'
                                                      'div/tree-node-collection/div/tree-node[1]/div')
        suggested = suggested.text.split('\n')
        for el in suggested:
            if el != 'Suggested Release':
                self.suggested_versions.append(el.replace('(MD)', '').replace('(ED)', ''))

    def get_info(self):
        self.get_platform()
        self.get_suggested()

        count = 1
        for ver in self.suggested_versions:
            self.driver.get(f'{self.ios_url}{ver}')

            # Wait for the page to load and check if version is available
            try:
                wait = WebDriverWait(self.driver, 5)
                wait.until(EC.presence_of_element_located((By.ID, "image-list")))
            except:
                continue

            # Hover over the file name
            file_name = self.driver.find_element_by_xpath("//span[@class='pointer text-darkgreen']")
            self.driver.execute_script("arguments[0].scrollIntoView();", file_name)
            ActionChains(self.driver).move_to_element(file_name).perform()

            # Wait for the popup to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "image-overlay-table")))

            # Find the values
            release_notes = self.driver.find_element_by_xpath('//app-root/div/main/div/div/app-release-page/div/div[2]/'
                                                              'app-image-details/div[1]/div/div/div[2]/'
                                                              'release-notes-component/div/ul/li/a')
            data_in_the_bubble = self.driver.find_element_by_id("image-overlay-table")
            version = data_in_the_bubble.find_element_by_xpath('//table[@id="image-overlay-table"]/tbody/tr[2]/td[2]')
            release_date = data_in_the_bubble.find_element_by_xpath('//table[@id="image-overlay-table"]/tbody/tr[3]/td[2]')
            bin_name = data_in_the_bubble.find_element_by_xpath('//table[@id="image-overlay-table"]/tbody/tr[4]/td[2]')
            md5 = data_in_the_bubble.find_element_by_xpath('//table[@id="image-overlay-table"]/tbody/tr[7]/td[2]')

            # Add the values as a list entry
            if count == 1:
                self.outputs1['version'] = version.text
                self.outputs1['bin_name'] = bin_name.text
                self.outputs1['release_date'] = release_date.text
                self.outputs1['md5'] = md5.text
                self.outputs1['release_notes'] = release_notes.get_attribute("href")
                self.outputs1['download_url'] = self.ios_url + ver
            else:
                self.outputs2['version'] = version.text
                self.outputs2['bin_name'] = bin_name.text
                self.outputs2['release_date'] = release_date.text
                self.outputs2['md5'] = md5.text
                self.outputs2['release_notes'] = release_notes.get_attribute("href")
                self.outputs2['download_url'] = self.ios_url + ver
            count += 1

    def __repr__(self):
        pass

    def quit(self):
        self.driver.quit()


web = WebPage()
web.get_info()
web.quit()

print(f'Cisco suggested releases for the {web.platform} are:')
print(f'Version: {web.outputs1.get("version")}\n'
      f'File name: {web.outputs1.get("bin_name")}\n'
      f'Release date: {web.outputs1.get("release_date")}\n'
      f'MD5: {web.outputs1.get("md5")}\n'
      f'Release notes: {web.outputs1.get("release_notes")}\n'
      f'Download link: {web.outputs1.get("download_url")}\n\n')

print(f'Version: {web.outputs2.get("version")}\n'
      f'File name: {web.outputs2.get("bin_name")}\n'
      f'Release date: {web.outputs2.get("release_date")}\n'
      f'MD5: {web.outputs2.get("md5")}\n'
      f'Release notes: {web.outputs2.get("release_notes")}\n'
      f'Download link: {web.outputs2.get("download_url")}\n')
