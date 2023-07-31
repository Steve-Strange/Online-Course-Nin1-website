from WebCrawler import Bilibili_pro
from WebCrawler.Bilibili import Bilibili
from WebCrawler.Bilibili_pro import Bilibili_pro
from WebCrawler.Chinaooc import Chinaooc
from WebCrawler.CNMOOC import CNMOOC
from WebCrawler.HDXol import HDXol
from WebCrawler.iCourse import iCourse
from WebCrawler.iMOOC import iMOOC
from WebCrawler.NetEase import NetEase
from WebCrawler.XTol import XTol

class INDEX:
    #href, name, cover, detail, play_num, comments_num, score, time_start, time_span
    web = 0
    name = 1
    cover = 2
    introduction = 3
    viewer_num = 4
    comments_num = 5
    score = 6
    time_start = 7
    duration = 8

SourceList = ["Bilibili", "Chinaooc", "CNMOOC", "HDXol", "iCourse", "iMOOC", "NetEase", "XTol"]
FuncList = [Bilibili_pro, Chinaooc, CNMOOC, HDXol, iCourse, iMOOC, NetEase, XTol]

def crawl_courses(keyword, src:str = None):
    '''
    爬取所有网站的课程.
    返回: dict{"source name": courseList...}
    '''
    ret = {}
    if src is None:
        # 全部爬
        for i in range(len(SourceList)):
            ret[SourceList[i]] = FuncList[i](keyword, 1)
    else:
        ret[src] = FuncList[SourceList.index(src)](keyword, 1)
    return ret