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
    with open ("final_output.txt", 'a', encoding='utf-8') as f:
        f.write(keyword)
        f.write(key)
        f.write(str(Bilibili(keyword,key)))
        f.write(str(Chinaooc(keyword, key)))
        f.write(str(CNMOOC(keyword, key)))
        f.write(str(HDXol(keyword, key)))
        f.write(str(iCourse(keyword, key)))
        f.write(str(iMOOC(keyword, key)))
        f.write(str(NetEase(keyword, key)))
        f.write(str(XTol(keyword, key)))
        f.write("success")
    
if __name__ == "__main__":
    time_start = time.time() #开始计时
    main()
    print("success")
    time_end = time.time()    #结束计时
    time_c= time_end - time_start   #运行所花时间
    print('time cost', time_c, 's')