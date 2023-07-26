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
    href, name, cover, detail, play_num, comments_num, score, time_start, time_span = 0, 0, 0, 0, 0, 0, 0, 0, 0

    chrome_options = Options()
    chrome_options.add_argument('headless')
    chrome_options.page_load_strategy = 'eager'
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=chrome_options)

    search_url = 'https://www.cnmooc.org/portal/frontCourseIndex/course.mooc?k=' + keyword
    driver.get(search_url)
    time.sleep(0.5)

    print("start scrapping")
    
    for i in range(1, 5):
        try:
            click_place = driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[2]/div/ul/li[" + str(i+2) + "]/a")
            ActionChains(driver).move_to_element(click_place).click(click_place).perform()
        except Exception:
            continue
        time.sleep(0.5)
        if(len(url_list) > 20):     # 最大数量
            break
        print("scrapping page " + str(i))
        
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        video_elements = soup.find_all(class_="view-item")
        time.sleep(0.3)
        
        for element in video_elements:
            if(len(url_list) > 20):
                break
            url = element.find('a')
        
            courseid = url.get('courseid')
            courseopenid = url.get('courseopenid')
            
            href = 'https://www.cnmooc.org/portal/course/' + courseid + '/' + courseopenid + '.mooc'
            
            name = element.find(class_ = "view-title substr").get_text().replace('\n', '').replace('\t', '')[:40].replace(' ','')
            
            try:
                play_num = int(element.find(class_ = 'progressbar-text').get_text().split(' ')[0])
                cover = element.find('img').get('src')
            except Exception:
                continue
            
            header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36", 
            "Cookie": "your cookie"} 

            if(href.find('https:') == -1):
                href = "https:" + href
            
            res = requests.get(href, headers=header)
            res.encoding = res.apparent_encoding
            soup2 = BeautifulSoup(res.text, "lxml")
            time.sleep(0.1)
            try:
                detail = soup2.find(class_ = "para-row").get_text().strip()
            except Exception:
                continue
            try:
                time.sleep(0.1)
                time_start = soup2.find(class_ = "view-time").get_text().strip().replace('\t', '')
                time_start = time_start[time_start.find('—') - 11 : time_start.find('—') -1]
            except Exception:
                time_start = ""
            print(href)
            
            url_list.append([href, name, cover, detail, play_num, comments_num, score, time_start, time_span])
        
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
    
    return url_list

if __name__ == "__main__":
    final_list = HDXol(input(), input())
    print(final_list)