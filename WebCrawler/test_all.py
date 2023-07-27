from Bilibili import *
from Chinaooc import *
from CNMOOC import *
from HDXol import *
from iCourse import *
from iMOOC import *
from NetEase import *
from XTol import *
import time

keyword = input()
key = input()

def main():
    print(Bilibili(keyword,key))
    print(Chinaooc(keyword, key))
    print(CNMOOC(keyword, key))
    print(HDXol(keyword, key))
    print(iCourse(keyword, key))
    print(iMOOC(keyword, key))
    print(NetEase(keyword, key))
    print(XTol(keyword, key))

    print("success")
    
if __name__ == "__main__":
    time_start = time.time() #开始计时
    main()
    time_end = time.time()    #结束计时
    time_c= time_end - time_start   #运行所花时间
    print('time cost', time_c, 's')