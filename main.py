from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from tkinter import *
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
outputs1 = {}
outputs2 = {}


class WebPage:
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('log-level=3')
        self.driver = webdriver.Chrome("chromedriver.exe", options=self.options)

        self.suggested_versions = []
        self.ios_url = ''

    def get_suggested(self, model, ios_type):
        if model in IOS_VERSIONS:
            self.ios_url = f'https://software.cisco.com/download/home/{IOS_VERSIONS[model]}/type/{ios_type}/release/'
        else:
            self.ios_url = f'https://software.cisco.com/download/home/{IOSXE_VERSIONS[model]}/type/{ios_type}/release/'

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

    def get_info(self, model, ios_type):
        self.get_suggested(model, ios_type)

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
                outputs1['version'] = version.text
                outputs1['bin_name'] = bin_name.text
                outputs1['release_date'] = release_date.text
                outputs1['md5'] = md5.text
                outputs1['release_notes'] = release_notes.get_attribute("href")
                outputs1['download_url'] = self.ios_url + ver
            else:
                outputs2['version'] = version.text
                outputs2['bin_name'] = bin_name.text
                outputs2['release_date'] = release_date.text
                outputs2['md5'] = md5.text
                outputs2['release_notes'] = release_notes.get_attribute("href")
                outputs2['download_url'] = self.ios_url + ver
                write_text(model)
            count += 1

    def __repr__(self):
        pass

    # function for closing the web driver
    def quit(self):
        self.driver.quit()


def write_text(model):
    output.delete('1.0', END)
    output.insert('end', f'Cisco suggested releases for the {model} are:\n'
                         f'Version: {outputs1.get("version")}\n'
                         f'File name: {outputs1.get("bin_name")}\n'
                         f'Release date: {outputs1.get("release_date")}\n'
                         f'MD5: {outputs1.get("md5")}\n'
                         f'Release notes: {outputs1.get("release_notes")}\n'
                         f'Download link: {outputs1.get("download_url")}\n\n\n\n'
                         f'Version: {outputs2.get("version")}\n'
                         f'File name: {outputs2.get("bin_name")}\n'
                         f'Release date: {outputs2.get("release_date")}\n'
                         f'MD5: {outputs2.get("md5")}\n'
                         f'Release notes: {outputs2.get("release_notes")}\n'
                         f'Download link: {outputs2.get("download_url")}\n')


# Function for closing the tkinter window
def close_window():
    window.destroy()


web = WebPage()

# Defining Tkinter parameters
window = Tk()
window.title('Cisco IOS/IOS-XE Web Scraper')
window.geometry("1100x400")
window.config(background="white")

# Create buttons, labels and a text box
ios_label = Label(window, text='IOS platforms')
iosxe_label = Label(window, text='IOS-XE platforms')
output = Text(height=320, width=250, wrap='word')

dropdown1 = StringVar(window)
dropdown1.set("ISR1905")  # default value
dd1 = OptionMenu(window, dropdown1, *IOS_VERSIONS)

dropdown2 = StringVar(window)
dropdown2.set("ISR4221")  # default value
dd2 = OptionMenu(window, dropdown2, *IOSXE_VERSIONS)

ios_confirm = Button(window, text="Extract", command=lambda: web.get_info(dropdown1.get(), 280805680), width=10)
iosxe_confirm = Button(window, text="Extract", command=lambda: web.get_info(dropdown2.get(), 282046477), width=10)
button_exit = Button(window, text="Exit", command=close_window, width=10)

# Place the elements in the window
ios_label.place(x=10, y=10)
iosxe_label.place(x=10, y=70)
ios_confirm.place(x=140, y=32)
iosxe_confirm.place(x=140, y=92)
dd1.place(x=10, y=32)
dd2.place(x=10, y=92)
output.place(x=100, y=125)
button_exit.place(x=10, y=370)

# Let the windows wait for any commands
window.mainloop()
web.quit()
