from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from tkinter import *
from tkinter import ttk
import time
import threading
from devices import *


class WebPage:
    def __init__(self, output_box, progress_bar):
        self.output_box = output_box
        self.pb = progress_bar
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('log-level=3')
        self.driver = webdriver.Chrome(options=self.options)

        self.suggested_versions = []
        self.ios_url = ''
        self.prints = 0

    def get_suggested(self, model, ios_type):
        if model in IOS_VERSIONS:
            self.ios_url = f'https://software.cisco.com/download/home/{IOS_VERSIONS[model]}/type/{ios_type}/release/'
        else:
            self.ios_url = f'https://software.cisco.com/download/home/{IOSXE_VERSIONS[model]}/type/{ios_type}/release/'

        # Open url to the chosen device.
        self.driver.get(self.ios_url)

        # Get suggested versions names.
        time.sleep(1)
        suggested = self.driver.find_element('xpath', '//app-root/div/main/div/div/app-release-page/div/div[1]/'
                                                      'app-release-details/nav/div[4]/tree-root/tree-viewport/div/'
                                                      'div/tree-node-collection/div/tree-node[1]/div')
        suggested = suggested.text.split('\n')
        for el in suggested:
            if el != 'Suggested Release':
                self.suggested_versions.append(el.replace('(MD)', '').replace('(ED)', ''))

    def get_info(self, model, ios_type):
        self.pb.start()
        self.output_box.delete('1.0', END)
        self.get_suggested(model, ios_type)

        for ver in self.suggested_versions:
            self.driver.get(f'{self.ios_url}{ver}')

            # Wait for the page to load and check if version is available
            try:
                wait = WebDriverWait(self.driver, 5)
                wait.until(EC.presence_of_element_located((By.ID, "image-list")))
            except:
                continue

            # Hover over the file name
            file_name = self.driver.find_element('xpath', "//span[@class='pointer text-darkgreen']")
            self.driver.execute_script("arguments[0].scrollIntoView();", file_name)
            ActionChains(self.driver).move_to_element(file_name).perform()

            # Wait for the popup to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "image-overlay-table")))

            # Find the values
            release_notes = self.driver.find_element('xpath', '//app-root/div/main/div/div/app-release-page/div/div[2]/'
                                                              'app-image-details/div[1]/div/div/div[2]/'
                                                              'release-notes-component/div/ul/li/a')
            data_in_the_bubble = self.driver.find_element('id', "image-overlay-table")
            version = data_in_the_bubble.find_element('xpath', '//table[@id="image-overlay-table"]/tbody/tr[2]/td[2]')
            release_date = data_in_the_bubble.find_element('xpath',
                                                           '//table[@id="image-overlay-table"]/tbody/tr[3]/td[2]')
            bin_name = data_in_the_bubble.find_element('xpath', '//table[@id="image-overlay-table"]/tbody/tr[4]/td[2]')
            md5 = data_in_the_bubble.find_element('xpath', '//table[@id="image-overlay-table"]/tbody/tr[7]/td[2]')

            outputs = {'version': version.text, 'bin_name': bin_name.text, 'release_date': release_date.text,
                       'md5': md5.text, 'release_notes': release_notes.get_attribute("href"),
                       'download_url': self.ios_url + ver}
            self.print_info(outputs, len(self.suggested_versions), model)

    def print_info(self, outputs, num_versions, model):
        if self.prints == 0:
            self.output_box.insert('end', f'Cisco suggested releases for the {model} are:\n')

        self.output_box.insert('end', f'Version: {outputs.get("version")}\n'
                                      f'File name: {outputs.get("bin_name")}\n'
                                      f'Release date: {outputs.get("release_date")}\n'
                                      f'MD5: {outputs.get("md5")}\n'
                                      f'Release notes: {outputs.get("release_notes")}\n'
                                      f'Download link: {outputs.get("download_url")}\n\n')
        self.prints += 1

        if self.prints == num_versions:
            self.pb.stop()
            self.driver.close()

    def __repr__(self):
        pass


# Function for closing the tkinter window
def close_window():
    window.destroy()


window = Tk()
# Defining Tkinter parameters
window.title('Cisco IOS/IOS-XE Web Scraper')
window.geometry("1107x662")
window.config(background="white")

# Create elements
ios_label = Label(window, text='IOS platforms')
iosxe_label = Label(window, text='IOS-XE platforms')
output = Text(height=30, width=113, wrap='word')
pb = ttk.Progressbar(window, orient='horizontal', mode='indeterminate', length=700)

ios_confirm = Button(window, text="Extract", command=lambda: threading.Thread(
    target=WebPage(output, pb).get_info, args=(ios_cb.get(), 280805680)).start(), width=10)

iosxe_confirm = Button(window, text="Extract", command=lambda: threading.Thread(
    target=WebPage(output, pb).get_info, args=(ios_xe_cb.get(), 282046477)).start(), width=10)

button_exit = Button(window, text="Exit", command=close_window, width=10)

ios_cb = ttk.Combobox(window)
ios_cb['values'] = [device for device in IOS_VERSIONS.keys()]
ios_cb['state'] = 'readonly'
ios_cb.set(list(IOS_VERSIONS.keys())[0])

ios_xe_cb = ttk.Combobox(window)
ios_xe_cb['values'] = [device for device in IOSXE_VERSIONS.keys()]
ios_xe_cb['state'] = 'readonly'
ios_xe_cb.set(list(IOSXE_VERSIONS.keys())[0])

# Place the elements in the window
ios_label.grid(column=0, row=0, sticky=W, padx=5, pady=3)
ios_cb.grid(column=0, row=1, sticky=W, padx=5, pady=0)
ios_confirm.grid(column=1, row=1, sticky=W, padx=5, pady=5)

iosxe_label.grid(column=0, row=2, sticky=W, padx=5, pady=3)
ios_xe_cb.grid(column=0, row=3, sticky=W, padx=5, pady=0)
iosxe_confirm.grid(column=1, row=3, sticky=W, padx=5, pady=5)

pb.grid(column=2, row=3, sticky=S)
button_exit.grid(column=0, row=4, sticky=S, padx=5, pady=5, rowspan=2)

output.grid(column=1, row=4, sticky=W, padx=5, pady=5, columnspan=4)

# Let the windows wait for any commands
window.mainloop()
