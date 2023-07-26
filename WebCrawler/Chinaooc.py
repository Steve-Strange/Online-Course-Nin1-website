from bs4 import BeautifulSoup
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

def Chinaooc(keyword, key):

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

    search_url = 'https://www.chinaooc.com.cn/search?keyword=' + keyword
    driver.get(search_url)
    time.sleep(0.3)
    
    click_place = driver.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div[2]/div/div[2]/div/div[3]/div[2]/button")
    ActionChains(driver).move_to_element(click_place).click(click_place).perform()
    time.sleep(0.1)

    print("start scrapping")
    
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    with open("output.txt", 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    video_elements = soup.find_all(class_="border-b border-gray-300")
    
    time.sleep(0.1)
    for element in video_elements:
        if(len(url_list) > 20):
            break
        href = "https://www.chinaooc.com.cn" + element.find('a').get('href')
        print(href)
        
        name = element.find(class_ = "inline-block font-bold text-link").get_text()
        cover = element.find('img').get('src')
        detail = element.find(class_ = "text-xs text-gray-500 mt-3 leading-5").get_text().strip()
        play_num = element.find(class_ = "align-bottom mr-5").get_text().replace("+", '').replace("少于", '')[:-3]
        play_num = ToNum(play_num)
        # print(name, cover, detail, play_num)

        driver.execute_script(js.format(href))
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(0.2)
        html_class = driver.page_source
        soup_class = BeautifulSoup(html_class, "lxml")

        time_start = soup_class.find_all(class_ = "table-td")[4].get_text().strip()[:10]
        
        print(time_start)
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

if __name__ == "__main__":
    final_list = Chinaooc(input(), input())
    print(final_list)