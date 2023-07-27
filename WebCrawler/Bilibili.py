from bs4 import BeautifulSoup
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import asyncio
from bilibili_api import video

async def Bilibili_async(keyword, key):

    href, name, cover, detail, play_num, comments_num, score, time_start, time_span = 0, 0, 0, 0, 0, 0, 0, 0, 0

    js = "window.open('{}','_blank');"
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("blink-settings=imagesEnabled=false")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=chrome_options)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Network.setBlockedURLs",{
        "urls":["*.flv*","*.png","*.jpg*","*.jepg*","*.gif*"]
    })

    search_url = 'https://search.bilibili.com/all?keyword=' + keyword
    driver.get(search_url)
    time.sleep(0.1)
    
    print("start scrapping")
    
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    with open("output.txt", 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    video_elements = soup.find(class_ = "video i_wrapper search-all-list").find_all(class_ = "bili-video-card__wrap __scale-wrap" )
    time.sleep(0.1)
    # find_class = soup.find(attrs={'class':'item-1'})
    
    url_list = []

    for element in video_elements:
        if(len(url_list) > 20):
            break
        url = element.find('a')
        
        href = "https:" + url.get('href')
        text = url.get_text(separator=' ').split(' ')
        if len(text[-1]) == 5:
            time_span = "00:" + text[-1]
        else:
            time_span = text[-1]
            
        time_start = element.find(class_ = "bili-video-card__info--date").get_text().strip()[2:]
        if (time_start == "昨天"):
            time_start = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
        if (time_start.find("前") != -1):
            continue
        if len(time_start) <= 5:
            time_start = "2023-" + time_start
        
        v = video.Video(bvid = str(href.split('/')[-2]))
        info = await v.get_info()

        name = info['title']
        cover = info['pic']
        detail = info['desc']
        play_num = info['stat']['view']
        comments_num = info['stat']['reply']
        
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

def Bilibili(keyword, key):
    return asyncio.get_event_loop().run_until_complete(Bilibili_async(keyword, key))

if __name__ == "__main__":
    final_list = Bilibili(input(), input())
    
    print(final_list)