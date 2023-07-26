from bs4 import BeautifulSoup
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

def Bilibili(keyword, key):

    href, name, cover, detail, play_num, comments_num, score, time_start, time_span = 0, 0, 0, 0, 0, 0, 0, 0, 0
    
    def ToNum(s):
        
        if(s.find("亿") != -1):
            s = int(float(s[0:len(s)-1]) * 100000000)
        elif(s.find("万") != -1):
            s = int(float(s[0:len(s)-1]) * 10000)
        else:
            s = int(s)

        return s

    js = "window.open('{}','_blank');"
    chrome_options = Options()
    chrome_options.add_argument('headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=chrome_options)

    search_url = 'https://search.bilibili.com/all?keyword=' + keyword
    driver.get(search_url)
    time.sleep(0.1)
    
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    with open("output.txt", 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    video_elements = soup.find_all(class_ = "bili-video-card__wrap __scale-wrap" )
    # find_class = soup.find(attrs={'class':'item-1'})

    url_list = []

    for element in video_elements:
        if(len(url_list) > 20):
            break
        url = element.find('a')
        
        cover = str(element.find(class_ = "v-img bili-video-card__cover")).split('><')[3].\
            replace("@672w_378h_1c_!web-search-common-cover.webp\" type=\"image/webp\"", '').\
                replace("source srcset=\"//", '')
        
        href = "https:" + url.get('href')
        print(href)
        text = url.get_text(separator=' ').split(' ')
        title = element.get_text()
        title = title[title.rfind(':')+3: len(title)].split(' · ')
        name = title[0]
        if len(title[1]) <= 5:
            time_start = "2023-" + title[1]
        
        play_num = ToNum(text[0])
        comments_num = ToNum(text[1])
        if len(text[2]) == 5:
            time_span = "00:" + text[2]
        else:
            time_span = text[2]
        
        driver.execute_script(js.format(href))
        time.sleep(0.5)
        driver.switch_to.window(driver.window_handles[-1])
        html_class = driver.page_source
        soup_class = BeautifulSoup(html_class, "lxml")

        detail = soup_class.find(class_ = "desc-info-text").get_text().replace('\n', '').replace('\r', '')
        
        url_list.append([href, name, cover, detail, play_num, comments_num, score, time_start, time_span])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    driver.quit()

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
    final_list = Bilibili(input(), input())
    print(final_list)