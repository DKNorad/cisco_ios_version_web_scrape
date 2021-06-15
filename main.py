from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

CHROMEDRIVER_PATH = "chromedriver.exe"
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument('log-level=3')
driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)

platform = input('Please choose platform(282907259/type/280805680): ')
ios_type = input('Please choose IOS type(IOS or IOS-XE): ')
versions = []
if ios_type == 'IOS':
    start, end = input('Please choose start and end version(5/7 for 15.5.3M/15.7.3M): ').split('/')
    for num in range(int(start), int(end) + 1):
        for num2 in range(0, 11):
            if num2 == 0:
                versions.append(f'15.{num}.3M')
            else:
                versions.append(f'15.{num}.3M{num2}')
elif ios_type == 'IOS-XE':
    six_or_seven = input('Please choose 16 or 17: ')
    if six_or_seven == '16':
        start, end, max_v = input('Please choose START/END/MAX version(3/12/8 for 16.3.8/16.12.8): ').split('/')
        for num in range(int(start), int(end) + 1):
            for num2 in range(1, int(max_v) + 1):
                if num == 3:
                    v_name = 'Denali'
                elif num == 4 or num == 5 or num == 6:
                    v_name = 'Everest'
                elif num == 7 or num == 8 or num == 9:
                    v_name = 'Fuji'
                elif num == 10 or num == 11 or num == 12:
                    v_name = 'Gibraltar'
                versions.append(f'{v_name}-16.{num}.{num2}')
    elif six_or_seven == '17':
        start, end, max_v = input('Please choose START/END/MAX version(1/3/8 for 17.1.8/17.3.8): ').split('/')
        for num in range(int(start), int(end) + 1):
            for num2 in range(1, int(max_v) + 1):
                versions.append(f'Amsterdam-17.{num}.{num2}')

outputs = []
for ver in versions:
    driver.get(f"https://software.cisco.com/download/home/{platform}/release/{ver}")

    # Wait for the page to load and check if version is available
    try:
        wait = WebDriverWait(driver, 3)
        wait.until(EC.presence_of_element_located((By.ID, "image-list")))
    except:
        continue

    # Hover over the file name
    file_name = driver.find_element_by_xpath("//span[@class='pointer text-darkgreen']")
    hov = ActionChains(driver).move_to_element(file_name)
    hov.perform()

    # Wait for the popup to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "image-overlay-table")))

    # Find the values
    data_in_the_bubble = driver.find_element_by_id("image-overlay-table")
    version = data_in_the_bubble.find_element_by_xpath('//table[@id="image-overlay-table"]/tbody/tr[2]/td[2]')
    md5 = data_in_the_bubble.find_element_by_xpath('//table[@id="image-overlay-table"]/tbody/tr[7]/td[2]')

    # Add the values as a list entry
    outputs.append(f'{version.text} - {md5.text}')
    print(f'Info for {version.text} collected')
driver.quit()

# export the values to a .txt file
with open('result.txt', 'w') as f:
    for entry in outputs:
        f.write('%s\n' % entry)

print('Program complete.')
