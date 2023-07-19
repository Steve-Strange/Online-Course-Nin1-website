'''
对数据库create, read, updata, delete operations.
基本就是create, delete.
'''
from User.models import UserProfile, UserGraphs, UserTags
from Neo4j.models import GraphRoot, KnowledgeBlock, Course, placeholder
from Utils.find import find_all_knowledge_in_graph, find_all_courses_in_knowledge
from Utils.file_operators import csv_loader


class Creator:
    @staticmethod
    def create_graph(name = None, intro = None, file = None):
        '''
        创建一张新的知识图谱, 可以是空的，也可以是根据文件加载来的.
        name: 图的名字，不指定则为默认.
        intro: 图的introduction, 不指定为空.
        file: 指定则为从csv中导入，否则建立一个只有空节点的图.
        返回：新图的GraphRoot节点.
        '''
        '''
        TODO: 判断文件种类，简单的csv还是（如果后面实现了）自己导出的json.
        '''
        if file is not None:
            # TODO: 通过uid找到节点，并做爬取!这里不能直接return.
            return csv_loader(file, name, intro)
        # 创建一个空图. 只有一个无效的知识节点.
        root = GraphRoot()
        if name is not None:
            root.graph_name = name
        if intro is not None:
            root.introduction = intro
        root.save()
        know = KnowledgeBlock(name = placeholder).save()
        root.rel_knowledge.connect(know)
        return root


    @staticmethod
    def create_knowledge(name:str = None, intro:str = None, crawl:bool = True):
        '''
        创建一个新的知识节点，并且爬取课程.
        crawl: 是否爬取，默认是.
        返回：knowledge的节点本身.
        '''
        know = KnowledgeBlock(name = placeholder if name is None else name)
        if intro is not None:
            know.introduction = intro
        know.save()
        if crawl:
            # TODO : 对节点做爬取.
            pass
        return know


    @staticmethod
    def create_course(knowledge:KnowledgeBlock, name:str, web:str, source:str="unknown", introduction:str=""):
        '''
        knowledge: 这个课程属于哪个知识点.它在图中的父亲.
        返回:这个course节点
        '''
        course = Course(name=name, web=web, source=source, introduction=introduction).save()
        knowledge.rel_courses.connect(course)
        return course


class Deleter:
    @staticmethod
    def delete_graph(root:GraphRoot):
        '''
        删除以这个GraphRoot为根的图。注意，连这个root也会被删除!
        返回：这个root原本的uid. 注意返回的时候这个uid已经失效，因为这个root已经被删除!
        '''
        knowlist = find_all_knowledge_in_graph(root)
        for know in knowlist:
            courselist = find_all_courses_in_knowledge(know)
            for course in courselist:
                course.delete()
            know.delete()
        uid = root.uid
        root.delete()
        return uid
    

    @staticmethod
    def delete_knowledge(knowledge:KnowledgeBlock):
        '''
        删除这个知识点节点以及它相关的所有课程.
        返回它原本的uid, 返回的时候这个节点已经被删除了.
        '''
        courselist = find_all_courses_in_knowledge(knowledge)
        for course in courselist:
            course.delete()
        uid = knowledge.uid
        knowledge.delete()
        return uid
    

    @staticmethod
    def delete_course(course:Course):
        uid = course.uid
        course.delete()
        return uid