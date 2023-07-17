import requests 
from bs4 import BeautifulSoup

def ToNum(s):
    
    if(s.find("亿") != -1):
        s = int(float(s[0:len(s)-1]) * 100000000)
    elif(s.find("万") != -1):
        s = int(float(s[0:len(s)-1]) * 10000)
    else:
        s = int(s)

    return s

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36", 
         "Cookie": "your cookie"} 

keyword = input()
key = input()

search_url = 'https://search.bilibili.com/all?keyword=' + keyword

res = requests.get(search_url, headers=header) 

soup = BeautifulSoup(res.text, "lxml")

with open("output.txt", 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

video_elements = soup.find_all(class_ = "bili-video-card__wrap __scale-wrap" )
# find_class = soup.find(attrs={'class':'item-1'})

url_list = []

for element in video_elements:
    
    url = element.find('a')
    # print(url.get('href'), url.get_text(separator='\n'))
    
    href = url.get('href')
    text = url.get_text(separator=' ').split(' ')
    title = element.get_text()
    title = title[title.rfind(':')+3: len(title)].split(' · ')
    if len(title[1]) <= 5:
        title[1] = "2023-" + title[1]
    
    text[0] = ToNum(text[0])
    text[1] = ToNum(text[1])
    
    url_list.append([href, text, title])

if key == "0":
    url_list.sort(key=lambda x: float(x[1][0] + x[1][1] * 100), reverse=True)       # 默认，综合排序 播放量 + 100 * 弹幕数
elif key == "1":
    url_list.sort(key=lambda x: float(x[1][0]), reverse=True)   # 播放量
elif key == "2":
    url_list.sort(key=lambda x: float(x[1][1]), reverse=True) # 弹幕数量
elif key == "3":
    url_list.sort(key=lambda x: x[1][2], reverse=True) # 视频总时长
else:
    url_list.sort(key=lambda x: x[2][1], reverse=True) # 视频发布日期

for elem in url_list:
    print(elem)