from django.db import models
from neomodel import (StructuredNode, StructuredRel, StringProperty, IntegerProperty, RelationshipTo,
                      UniqueIdProperty)

# 这个字符串表示这个节点是空的，是无效的.
# 如果节点的名称是这个的话，就不要对它爬取内容了.
placeholder = "Empty Node"

# Create your models here.
class TagNode(StructuredNode):
    uid = UniqueIdProperty()
    tag = StringProperty(default = "")    
    
    def __str__(self):
        if self.tag == "":
            return "no tag."
        else:
            return str(self.tag)
        

class TagEdge(StructuredRel):
    '''
    连接课程和课程的有向边.
    '''
    uid = UniqueIdProperty()
    tag = StringProperty(default = "")

    def __str__(self) -> str:
        if self.tag == "":
            return "no tag."
        else:
            return str(self.tag)
        

class KnowledgeBlock(TagNode):
    '''
    知识图谱上的节点.
    '''
    name = StringProperty(required = True)
    introduction = StringProperty(default = "")
    rel_knowledge = RelationshipTo("KnowledgeBlock", "relevant knowledge", model=TagEdge)
    rel_courses = RelationshipTo("Course", "courses about the knowledge")

    def __str__(self):
        tag = super().__str__()
        ret = str(self.name)
        if tag != "no tag.":
            ret += ("\n" + tag)
        return ret


class GraphRoot(TagNode):
    graph_name = StringProperty(default = "Unnamed Knowledge Graph")
    introduction = StringProperty(default = "")
    rel_knowledge = RelationshipTo("KnowledgeBlock", "Graph") # 连接到一个图的节点上.
    
    def __str__(self):
        return str(self.graph_name)
    

class Course(TagNode):
    '''
    网课的条目.
    '''
    name = StringProperty(required = True)
    web = StringProperty(required = True)
    source = StringProperty(default = "unknown")  # 来源，尽量用xx大学来表示.  
    duration = IntegerProperty(default=-1)  #-1表示缺少该信息.
    viewer_num = IntegerProperty(default=-1)# 观看/学习人数.
    introduction = StringProperty(default = "")  # 简介.
    # 封面图片...等等其它可以爬到的.