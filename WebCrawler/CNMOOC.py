from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

def CNMOOC(keyword, key):

    url_list = []
    href, name, cover, detail, play_num, comments_num, score, time_start, time_span = 0, 0, 0, 0, 0, 0, 0, 0, 0

    js = "window.open('{}','_blank');"
    chrome_options = Options()
    chrome_options.add_argument('headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=chrome_options)

    search_url = "https://www.icourse163.org/search.htm?search=" + keyword
    driver.get(search_url)
    time.sleep(0.1)
    click_place = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[2]/div[2]/div/div[6]/div[1]/ul/li[2]")
    ActionChains(driver).move_to_element(click_place).click(click_place).perform()
    time.sleep(0.1)

    print("start scrapping")

    for i in range(1, 5):
        if(len(url_list) > 20):     # 最大数量
            break
        print("scrapping page " + str(i))

        try:
            click_place = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[2]/div[2]/div/div[6]/div[2]/div[2]/ul/li[" + str(i + 1) + "]")
            ActionChains(driver).move_to_element(click_place).click(click_place).perform()
        except Exception:
            continue
        time.sleep(0.5)

        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        with open("output.txt", 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

        video_elements = soup.find_all(class_="u-clist f-bgw f-cb f-pr j-href ga-click")
        time.sleep(0.1)

        for element in video_elements:
            if(len(url_list) > 20):
                break
            url = element.find('a')

            href = url.get('href')
            if href.find("kaoyan") != -1 or href.find("undefined") != -1:
                continue
            
            name = url.get_text(separator=' ')
            text_detail = element.find("span", class_ = "p5 brief f-ib f-f0 f-cb").get_text()
            
            if name.find(keyword) == -1 and text_detail.find(keyword) == -1:        # 筛选是否有关键词 （同义词问题）
                continue

            price_element = element.find("span", class_="price")
            attendance_element = element.find("span", class_="hot")
            attendance_num = int(attendance_element.get_text()[0:-3])
            
            if price_element is not None and price_element.get_text() != "免费":
                continue

            print(href)
            
            driver.execute_script(js.format(href))
            driver.switch_to.window(driver.window_handles[-1])

            try:
                click_place = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]")
                ActionChains(driver).move_to_element(click_place).click(click_place).perform()
            except Exception:
                continue
            time.sleep(0.1)
            html_class = driver.page_source
            soup_class = BeautifulSoup(html_class, "lxml")

            comments_element = soup_class.find(class_ = "ux-mooc-comment-course-comment_head")

            if comments_element == None:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            
            comments = comments_element.get_text().replace('\n','')
            
            try:
                comments_score = float(comments[0: 3])
            except Exception:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
        
            try:
                comments_num = int(comments[5: -4])
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

    for elem in url_list:
        print(elem)

CNMOOC(input(), input())