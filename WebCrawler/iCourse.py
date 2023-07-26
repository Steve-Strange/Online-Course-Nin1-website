from bs4 import BeautifulSoup
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

def iCourse(keyword, key):

    url_list = []
    href, name, cover, detail, play_num, comments_num, score, time_start, time_span = 0, 0, 0, 0, 0, 0, 0, 0, 0

    chrome_options = Options()
    chrome_options.add_argument('headless')
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
        if(len(url_list) > 20):     # 最大数量
            break
        print("scrapping page " + str(i))
        
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        video_elements = soup.find_all(class_="icourse-item-modulebox")
        time.sleep(0.1)
        
        for element in video_elements:
            if(len(url_list) > 20):
                break
            url = element.find('a')
            
            href = url.get('href')
            
            if(href.find("icourse163") != -1):      # 中国慕课的。。
                continue;
            
            cover = element.find('img').get('src')
            
            text = element.get_text().split('\n')
            name = text[9]
        
            
            header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36", 
            "Cookie": "your cookie"} 

            if(href.find('https:') == -1):
                href = "https:" + href
            
            print(href)
            
            res = requests.get(href, headers=header)
            res.encoding = res.apparent_encoding
            soup2 = BeautifulSoup(res.text, "lxml")
            
            detail = soup2.find(class_ = "course-text").get_text().strip()
            
            try:
                class_info = soup2.find(class_="course-information boxstyle").get_text().split('\n')
            except Exception:
                continue;
            
            play_num = int(class_info[class_info.index('学习人数:') + 1])
            comments_num = int(class_info[class_info.index('评论数:') + 1])
            time_span = class_info[class_info.index('课程学时:') + 1][:-2] + "小时"
            
            
            url_list.append([href, name, cover, detail, play_num, comments_num, score, time_start, time_span])
        
        try:
            if i == 1:
                click_place = driver.find_element(By.XPATH, "/html/body/div[1]/section/div/div[2]/div/div/a[7]")
            else:
                click_place = driver.find_element(By.XPATH, "/html/body/div[1]/section/div/div[2]/div/div/a[9]")
            ActionChains(driver).move_to_element(click_place).click(click_place).perform()
        except Exception:
            continue
        
        time.sleep(0.1)

    if len(url_list) == 0:
        print("No results")
        exit()

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

if __name__ == "__main__":
    final_list = iCourse(input(), input())
    print(final_list)