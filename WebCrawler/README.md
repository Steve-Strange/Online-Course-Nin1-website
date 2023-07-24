# The readme of Webcrawler

## How to use

- 8个网站，每个网站文件中的函数就是文件名
- from xxx import *
- class_list = xxx(input(), input())
- 两个输入分别是关键词和排序方式的序号从0-5，可以再添加，但需要设置字典对应等

    ```python
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
    ```

- 函数返回值为一个list，每个元素是一个list，包含视频的信息，链接，名称，封面链接，简介，播放量，评论数，评分，发布时间，时长。
- 其中播放量和评论数为int类型，评分为float类型，其他为str类型

    ```python
        url_list.append([href, name, cover, detail, play_num, comments_num, score, time_start, time_span])
    ```

## debug

- print
  - start scrapping
  - scrapping page 1 (如果需要翻页)
  - url1, url2, url3...
  - scrapping page 2
  - ...
  - end scrapping

- selenium 页面模拟显示
  - 将15行 chrome_options.add_argument('headless') 启动无头模式注释即可
