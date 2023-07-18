# 创建一个简单的临时知识图谱，以供调试.  
# 如果删掉了，直接回来运行这个脚本即可.
'''
删除所有节点.
MATCH (n)
OPTIONAL MATCH (n)-[r]-()
DELETE n,r
'''
from neomodel import config
from models import KnowledgeBlock, Course, GraphRoot

with open('../developer_sign.txt', 'r') as f:
    username = f.readline().strip()
    pwd = f.readline().strip()


config.DATABASE_URL = 'bolt://'+username+':'+pwd+'@localhost:7687/course-recom'  
config.MAX_CONNECTION_POOL_SIZE = 50
config.AUTO_INSTALL_LABELS = False
config.ENCRYPTED = False  # Neo4j默认不 Encrypted.
config.FORCE_TIMEZONE = False

# 创建一个非常简单的知识图谱，两个节点，每个节点两个课程.
simple_root = GraphRoot(graph_name="TestGraph")
simple_root.tag = "this is a graph tag only for test"
simple_root.save()
know1 = KnowledgeBlock(name = "TestKnowledge1")
know1.tag = "this is the tag of know1, just for test"
know1.save()
know2 = KnowledgeBlock(name = "TestKnowledge2").save()
courses = []
webs = ["https://www.bilibili.com/", "https://docs.djangoproject.com/zh-hans/4.2/",
        "https://www.runoob.com/django/django-tutorial.html",
        "https://www.runoob.com/bootstrap5/bootstrap5-tutorial.html"]
for i in range(1, 5):
    tmp_course = Course(name="TestCourse%d"%(i), web=webs[i-1])
    tmp_course.name = "TestCourse%d"%(i)
    tmp_course.source = "Source%d"%(i)
    if i != 1:
        tmp_course.duration = i
    if i != 2:
        tmp_course.viewer_num = i
    tmp_course.introduction = "only for test"
    #tmp_course.save()
    courses.append(tmp_course)
courses[1].tag = "this is the tag of course2, only for test"
courses[3].tag = "this is the tag of course4, only for test"
# courses[1].save()
# courses[3].save()
for i in courses:
    i.save()
    print("course saved")

# 建立关系.
simple_root.rel_knowledge.connect(know1)
know1.rel_knowledge.connect(know2)
know1.rel_courses.connect(courses[0])
know1.rel_courses.connect(courses[1])
know2.rel_courses.connect(courses[2])
know2.rel_courses.connect(courses[3])