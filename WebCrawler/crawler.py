from WebCrawler.Bilibili import BiliBili
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

SourceList = ["BiliBili", "Chinaooc", "CNMOOC", "HDXol", "iCourse", "iMOOC", "NetEase", "XTol"]
FuncList = [BiliBili, Chinaooc, CNMOOC, HDXol, iCourse, iMOOC, NetEase, XTol]

def crawl_courses(keyword):
    '''
    爬取所有网站的课程.
    返回: dict{"source name": courseList...}
    '''
    ret = {}
    for i in range(len(SourceList)):
        ret[SourceList[i]] = FuncList[i](keyword, 1)
    return ret