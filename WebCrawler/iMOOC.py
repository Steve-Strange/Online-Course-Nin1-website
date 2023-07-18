from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

def iMOOC(keyword, key):

    url_list = []
    href, name, cover, detail, play_num, comments_num, score, time, time_span = 0, 0, 0, 0, 0, 0, 0, 0, 0
    keyword = input()
    key = input()

    js = "window.open('{}','_blank');"
    chrome_options = Options()
    chrome_options.add_argument('headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=chrome_options)

    search_url = "https://www.imooc.com/search/?type=course&words=" + keyword
    driver.get(search_url)
    time.sleep(0.1)

    try:
        click_place = driver.find_element(By.XPATH, "/html/body/div[5]/div/div[3]/div[1]/div[1]/div[3]/div[1]/p")
        ActionChains(driver).move_to_element(click_place).click(click_place).perform()
        time.sleep(0.1)
        click_place = driver.find_element(By.XPATH, "/html/body/div[5]/div/div[3]/div[1]/div[1]/div[3]/div[1]/div/ul/li[3]")
        ActionChains(driver).move_to_element(click_place).click(click_place).perform()
        time.sleep(0.1)
    except Exception:
        print("No results")
        exit()

    print("start scrapping")

    for i in range(1, 4):
        if(len(url_list) > 20):
            break
        print("scrapping page " + str(i))
        try:
            click_place = driver.find_element(By.XPATH, "/html/body/div[5]/div/div[3]/div[1]/div[4]/a[" + str(i) + "]")
            ActionChains(driver).move_to_element(click_place).click(click_place).perform()
        except Exception:
            continue
        time.sleep(0.1)
        
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        with open("output.txt", 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

        video_elements = soup.find_all(class_="search-item js-search-item clearfix")
        time.sleep(0.3)

        for element in video_elements:
            if(len(url_list) > 20):
                break
            url = element.find('a')
            href = "https://www.imooc.com/learn/" + url.get('href')[6:]
            print(href)
            
            text = element.get_text()[8:-2].split(' ')
            
            name = text[0]
            detail = text[3]
            level = text[-3][-2:]
            dict_level = {'基础': 1, '初阶': 2, '进阶': 3, '高阶': 4}
            attendance_num = int(text[-1])
            
            driver.execute_script(js.format(href))
            driver.switch_to.window(driver.window_handles[-1])

            try:
                click_place = driver.find_element(By.XPATH, "/html/body/div[5]/div[2]/div/ul/li[4]/a")
                ActionChains(driver).move_to_element(click_place).click(click_place).perform()
            except Exception:
                continue
            html_class = driver.page_source
            soup_class = BeautifulSoup(html_class, "lxml")

            try:
                comments = float(soup_class.find(class_ = "evaluation-score l").get_text().replace(" ", "").replace("\n", ""))
            except Exception:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            
            url_list.append([href, name, cover, detail, play_num, comments_num, score, time, time_span])
            
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

    for elem in url_list:
        print(elem)
        
iMOOC(input(), input())