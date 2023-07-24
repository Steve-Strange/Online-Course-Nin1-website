from bs4 import BeautifulSoup
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

def NetEase(keyword, key):

    def ToNum(s):
        
        if(s.find("亿") != -1):
            s = int(float(s[0:len(s)-1]) * 100000000)
        elif(s.find("万") != -1):
            s = int(float(s[0:len(s)-1]) * 10000)
        else:
            s = int(s)

        return s
    
    url_list = []
    href, name, cover, detail, play_num, comments_num, score, time_start, time_span = 0, 0, 0, 0, 0, 0, 0, 0, 0

    js = "window.open('{}','_blank');"
    chrome_options = Options()
    chrome_options.add_argument('headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=chrome_options)

    search_url = "https://open.163.com/newview/search/" + keyword
    driver.get(search_url)
    driver.execute_script('window.scrollBy(0,5000)')
    time.sleep(0.1)
    driver.execute_script('window.scrollBy(0,5000)')
    time.sleep(0.1)
    driver.execute_script('window.scrollBy(0,5000)')
    time.sleep(0.1)
    driver.execute_script('window.scrollBy(0,5000)')
    time.sleep(0.1)
    
    print("start scrapping")
    
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    with open("output.txt", 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    video_elements = soup.find_all(class_="type-card video-collection-card")
    
    time.sleep(0.1)
    
    for element in video_elements:
        if(len(url_list) > 20):
            break
        href = "https://open.163.com" + element.find('a').get('href')
        print(href)
        
        name = element.find(class_ = "subname").get_text()[:-5]
        cover = element.find('img').get('src')
        text = element.get_text().split(' ')
        play_num = ToNum(text[-1][:-3])
        time_span = text[-2]

        driver.execute_script(js.format(href))
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(0.2)
        html_class = driver.page_source
        soup_class = BeautifulSoup(html_class, "lxml")
        
        
        try:
            comments_num = soup_class.find_all(class_ = "comment-container__title")[1].get_text().strip()[5:-1]
        except Exception:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            continue
        
        url_list.append([href, name, cover, detail, play_num, comments_num, score, time_start, time_span])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    driver.quit()

    print("finish scrapping")

    if key == "0":
        url_list.sort(key=lambda x: x[1], reverse=True)   # 名称排序
    elif key == "1":
        url_list.sort(key=lambda x: float(x[4]), reverse=True)   # 播放量 / 参与用户数
    elif key == "2":
        url_list.sort(key=lambda x: float(x[5]), reverse=True) # 评论数量
    elif key == "3":
        url_list.sort(key=lambda x: float(x[6]), reverse=True) # 评分
    elif key == "4":
        url_list.sort(key=lambda x: x[7], reverse=True) # 视频发布日期
    else:
        url_list.sort(key=lambda x: x[8], reverse=True) # 视频时长

    if len(url_list) == 0:
        print("No results")
        exit()

    return url_list

final_list = NetEase(input(), input())
print(final_list)