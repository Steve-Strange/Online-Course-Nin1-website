from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

url_list = []
keyword = input()

js = "window.open('{}','_blank');"
chrome_options = Options()
# chrome_options.add_argument('headless')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=chrome_options)

search_url = "https://www.icourses.cn/web/sword/portalsearch/homeSearch"
driver.get(search_url)
time.sleep(0.1)

driver.find_element(By.ID, "searchInput").send_keys(keyword)
driver.find_element(By.ID, "searchInput").send_keys(Keys.ENTER)
time.sleep(0.5)

print("start scrapping")

for i in range(1, 5):
    if(len(url_list) > 30):     # 最大数量
        break
    print("scrapping page " + str(i))
    
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    video_elements = soup.find_all(class_="icourse-item-modulebox")
    time.sleep(0.1)
    
    for element in video_elements:
        if(len(url_list) > 30):
            break
        url = element.find('a')

        href = url.get('href')
        print(href)
        
        text = element.get_text().split('\n')
        name = text[9]
        class_type = text[12]
        teacher = text[15]

        print(name, class_type, teacher)
        url_list.append([href, name, class_type, teacher])
    
    try:
        if i == 1:
            click_place = driver.find_element(By.XPATH, "/html/body/div[1]/section/div/div[2]/div/div/a[7]")
        else:
            click_place = driver.find_element(By.XPATH, "/html/body/div[1]/section/div/div[2]/div/div/a[9]")
        ActionChains(driver).move_to_element(click_place).click(click_place).perform()
    except Exception:
         continue
    
    time.sleep(0.1)
