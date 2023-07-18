from bs4 import BeautifulSoup
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

def HDXol(keyword, key):

    url_list = []

    js = "window.open('{}','_blank');"
    chrome_options = Options()
    # chrome_options.add_argument('headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=chrome_options)

    search_url = 'https://www.cnmooc.org/portal/frontCourseIndex/course.mooc?k=' + keyword
    driver.get(search_url)
    time.sleep(0.1)

    print("start scrapping")
    
    for i in range(1, 5):
        if(len(url_list) > 50):     # 最大数量
            break
        print("scrapping page " + str(i))
        
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        video_elements = soup.find_all(class_="view-item")
        time.sleep(0.5)
        
        for element in video_elements:
            if(len(url_list) > 50):
                break
            url = element.find('a')

            courseid = url.get('courseid')
            courseopenid = url.get('courseopenid')
            
            href = 'https://www.cnmooc.org/portal/course/' + courseid + '/' + courseopenid + '.mooc'
            
            attend_num = int(element.find(class_ = 'progressbar-text').get_text().split(' ')[0])
            
            header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36", 
            "Cookie": "your cookie"} 

            if(href.find('https:') == -1):
                href = "https:" + href
            
            print(href)
            
            res = requests.get(href, headers=header)
            res.encoding = res.apparent_encoding
            soup2 = BeautifulSoup(res.text, "lxml")
            
            class_info = soup2.find(class_ ="view-favor subFavorite").get_text().replace('\r', '').split('\n')
            
            try:
                favor_num = int(class_info[1][:-2])
            except ValueError:
                continue
            
            url_list.append([href, attend_num, favor_num])
            
        try:
            click_place = driver.find_element(By.CLASS_NAME, "page-next")
            ActionChains(driver).move_to_element(click_place).click(click_place).perform()
        except Exception:
            continue
        
        time.sleep(0.5)

    driver.quit()
    print("finish scrapping")
    
    if key == "0":
        url_list.sort(key=lambda x: float(x[1] + x[2] * 30), reverse=True)       # 默认，综合排序
    elif key == "1":
        url_list.sort(key=lambda x: float(x[1]), reverse=True)   # 参与人数
    else:
        url_list.sort(key=lambda x: float(x[2]), reverse=True) # 收藏人数

    if len(url_list) == 0:
        print("No results")
        exit()

    for elem in url_list:
        print(elem)
        
HDXol(input(), input())