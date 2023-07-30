'''
Neo4j Graph类，包含一些操作.
'''
from typing import Any
from neomodel import db
import json
from jsonschema import validate, draft7_format_checker
from django.conf import settings
from os.path import join

from Neo4j.models import GraphRoot, KnowledgeBlock, Course, TagEdge
from Neo4j.node_operator import deleteTagNode
from Utils.file_operators import csv_loader, DisjointSets
from Utils.find import find_all_knowledge_in_graph, find_all_courses_in_knowledge, find_all_knowledge_from_knowledge
from User.models import UserProfile, UserGraphs, UserTags
from WebCrawler.crawler import SourceList, crawl_courses, INDEX


class Graph:
    with open("static/graphs/schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)
    '''
    对完整的图进行操作，包括导入导出、创建等.
    '''
    @staticmethod
    def validate(user:UserProfile, root_uid:str):
        '''
        检查这个图(uid)是否属于这个用户.
        '''
        try:
            tmp = user.usergraphs_set.get(root_uid = root_uid)
        except:
            return False
        return True
    

    # 给节点爬取课程.
    @staticmethod
    def crawlCoursesForKnowledge(knowledge:KnowledgeBlock, src:str = None):
        '''
        给knowledge节点爬取课程并且保存到数据库. 这里不做任何检查.
        '''
        courses = crawl_courses(knowledge.name, src)
        if src is None:
            srcarray = SourceList
        else:
            srcarray = [src]
        for src in srcarray:
            cList = courses[src]
            for course in cList:
                node = Course(name = course[INDEX.name], web = course[INDEX.web], source = src).save()
                if course[INDEX.comments_num]!=0 and not course[INDEX.comments_num]:
                    node.comments_num = course[INDEX.comments_num]
                if course[INDEX.cover]!=0 and not course[INDEX.cover]:
                    node.cover = course[INDEX.cover]
                if course[INDEX.duration]!=0 and not course[INDEX.duration]:
                    node.duration = course[INDEX.duration]
                if course[INDEX.introduction]!=0 and not course[INDEX.introduction]:
                    node.introduction = course[INDEX.introduction]
                if course[INDEX.score]!=0 and not course[INDEX.score]:
                    node.score = course[INDEX.score]
                if course[INDEX.time_start]!=0 and not course[INDEX.time_start]:
                    node.time_start = course[INDEX.time_start]
                if course[INDEX.viewer_num]!=0 and not course[INDEX.viewer_num]:
                    node.viewer_num = course[INDEX.viewer_num]
                node.save()
                knowledge.rel_courses.connect(node)
    

    def __init__(self, user:UserProfile, root:GraphRoot | str = None) -> None:
        '''
        指定图的根，或者不指定表示空图，将要进行创建等操作.
        root 是根的uid或者GraphRoot对象.
        '''
        self.user = user
        if isinstance(root, str):
            self.root = GraphRoot.nodes.get(uid = root)
        else:
            self.root = root
        self.knowledges = find_all_knowledge_in_graph(self.root) if self.root is not None else []
        for know in self.knowledges:
            print(know.name)


    def create_empty_graph(self, name:str, intro:str):
        '''
        用来创建一个空图，仅有一个Empty节点，不爬取课程
        返回新图的GraphRoot uid
        '''
        if not name:
            name = "unnamed"
        self.root = GraphRoot(graph_name = name, introduction = intro).save()
        usergraph = UserGraphs(root_uid = self.root.uid, user = self.user).save()
        emptyknow = KnowledgeBlock(name = "Empty").save()
        self.root.rel_knowledge.connect(emptyknow)
        self.knowledges += [emptyknow]
        return self.root.uid
    
    
    def import_json(self,json_file:str, crawl:bool=False):
        '''
        如果格式有误，会抛出异常.
        导入json格式的数据库. 总的格式: {
            "name":...
            "knowledges":[
                {
                    "name":...
                    "tag":...
                    "...":...
                }
                {
                    ...
                }
            ]
            "edges":[
                {
                    "from":knowledges中的下标.
                    "to":knowledges中的下标.
                    "tag":"...".
                }
            ]
            "courses":[
                {
                    "knowledge":上面的id.
                    "其它属性":...
                }
            ]
        }
        '''
        with open(json_file, "r", encoding="utf-8") as f:
            jf = json.load(f)  #jf是dict.
        validate(instance=jf, schema=Graph.schema, format_checker=draft7_format_checker)
        # 如果验证失败会直接抛出异常.
        # 通过了之后能直接进行下面的语句.
        knows = jf["knowledges"]
        edges = jf["edges"]
        courses = jf["courses"]  # 可以为空.
        self.knowledges = [None for i in range(len(knows))]
        for i in range(len(knows)):
            know = knows[i]
            # 根据后面对数据库的更改相应添加.
            self.knowledges[i] = KnowledgeBlock(name=know["name"], introduction=know["introduction"], tag=know["tag"]).save()
            # 刚创建的node可以通过.uid访问它的字符串，但是append到node之后就无效了,只有内存中的obj地址了!
            #self.knowledges.append(KnowledgeBlock.nodes.get(uid=node.uid))
            #self.knowledges.append(node)   # 应该是复制的锅.
            # neomodel原本创建的节点能用neomodel的transcation处理,但是复制之后的节点不能.
            # 要么直接在数组中创建，要么保留引用.
            if self.knowledges[i].tag:
                UserTags(tag_uid = self.knowledges[i].uid, user = self.user).save()
        ds = DisjointSets(range(len(self.knowledges)))
        for edge in edges:
            from_node = edge["from"]
            to_node = edge["to"]
            # start = KnowledgeBlock.nodes.get(uid=self.knowledges[from_node].uid)
            # end = KnowledgeBlock.nodes.get(uid=self.knowledges[to_node].uid)
            # rel = start.rel_knowledge.connect(end, tag = edge['tag'])
            rel = self.knowledges[from_node].rel_knowledge.connect(self.knowledges[to_node], {"tag":edge["tag"],})
            if rel.tag:
                UserTags(tag_uid = rel.uid, user = self.user).save()
            ds.union(from_node, to_node)
        if courses:
            # 有课程，不爬取.
            for course in courses:
                node = Course(
                    name = course["name"],
                    web = course["web"],
                    source = course["source"],
                    duration = course["duration"],
                    viewer_num = course["viewer_num"],
                    introduction = course["introduction"],
                    tag = course['tag'],
                    cover = course['cover'],
                    comments_num = course['comments_num'],
                    time_start = course['time_start'],
                    score = course['score']
                ).save()
                if course['cover']:
                    node.cover = course['cover']
                node.save()
                self.knowledges[course["knowledge"]].rel_courses.connect(node)
                if node.tag:
                    UserTags(tag_uid = node.uid, user = self.user).save()
        elif crawl:
            # 源文件没有课程，并且需要爬取.
            # 给知识节点爬取课程.
            for know in self.knowledges:
                Graph.crawlCoursesForKnowledge(know)

        # 注册给用户.
        self.root = GraphRoot()
        graph_name = jf.get("name", None)
        if graph_name is not None and graph_name != "":
            self.root.graph_name = graph_name
        self.root.save()
        for i in ds.get_roots():
            self.root.rel_knowledge.connect(self.knowledges[i])
        UserGraphs(root_uid = self.root.uid, user = self.user).save()
        # 结束.

    
    #@db.read_transaction
    def export_json(self, save_to_file:bool=True, get_tag:bool = False):
        '''
        将该图导出为json文件.保存到固定目录，文件名为graph的uid.json  
        如果save_to_file为false，就只返回字典.如果是True, 返回导出的json文件路径.
        '''
        knows_dicts = []
        edges_dicts = []
        courses_dicts = []
        knows = find_all_knowledge_in_graph(self.root)
        for i in range(len(knows)):
            knows_dicts.append({
                "name":str(knows[i].name),
                "tag":str(knows[i].tag) if get_tag else "",
                "introduction":str(knows[i].introduction),
            })
            for relknow in knows[i].rel_knowledge.all():
                rel = knows[i].rel_knowledge.relationship(relknow)
                edges_dicts.append({
                    "from":i,
                    "to":knows.index(relknow),
                    "tag":str(rel.tag) if get_tag else "",
                })
            for course in find_all_courses_in_knowledge(knows[i]):
                courses_dicts.append({
                    "knowledge":i,
                    "tag":str(course.tag) if get_tag else "",
                    "name" : str(course.name),
                    "web" : str(course.web),
                    "source" : str(course.source),
                    "duration" : str(course.duration),
                    "viewer_num" : str(course.viewer_num),
                    "introduction" : str(course.introduction),
                    "cover" : str(course.cover),
                    "comments_num" : str(course.comments_num),
                    "time_start" : str(course.time_start),
                    "score" : str(course.score),
                })
        
        ret = {
            "name":str(self.root.graph_name),
            "introduction":str(self.root.introduction),
            "tag":str(self.root.tag) if get_tag else "",
            "knowledges":knows_dicts,
            "edges":edges_dicts,
            "courses":courses_dicts,
        }
        if not save_to_file:
            return ret
        else:
            p = join(settings.GRAPH_JSON_DIR, "{}.json".format(self.root.uid))
            with open(join(p,'w')) as f:
                json.dump(ret, f, ensure_ascii=False)
            return p
        
    @db.read_transaction
    def get_str(self):
        '''
        获得echarts所需格式的两个字符串,返回
        node_datas, edge_datas.
        '''
        node_datas = "[\n"
        edge_datas = "[\n"
        for know in self.knowledges:
            node_str = \
            '''
            {{
                name:"{}",
                uid:"{}",
                intro:"{}",
                tag:"{}"
            }},\n
            '''.format(str(know.name).strip(), str(know.uid).strip(), str(know.introduction).strip(), str(know.tag).strip())
            node_datas += node_str
            for rel_node in know.rel_knowledge.all():
                edge_str = \
                '''
                {{
                    source:"{}",
                    target:"{}"
                }},\n
                '''.format(str(know.name).strip(), str(rel_node.name).strip())
                edge_datas += edge_str
        
        node_datas += "]"
        edge_datas += "]"
        return node_datas, edge_datas
    

    @db.write_transaction
    def create_node(self, name:str, introduction:str, crawl:bool = False):
        for know in self.knowledges:
            if know.name == name:
                return know   # 有重名的就不创建新的了.
        newknow = KnowledgeBlock(name = name, introduction = introduction).save()
        self.root.rel_knowledge.connect(newknow)
        self.knowledges += [newknow]
        if crawl:  # 需要爬取.
            Graph.crawlCoursesForKnowledge(newknow)
        return newknow
    

    # @db.write_transaction
    def delete_node(self, knowledge:KnowledgeBlock, validate:bool=True):
        '''
        删除这个节点以及所有相关的课程.
        这里不做检查了..
        返回被删除的节点原本的uid.
        '''
        # 检验确实有这个节点.
        if validate:
            valid = False
            for know in self.knowledges:
                if know.uid == knowledge.uid:
                    valid = True
                    break
            if not valid:
                raise "KnowledgeBlock does not exist in this graph"
        # 从graph当前节点中删除.
        ind = self.knowledges.index(knowledge)
        self.knowledges.pop(ind)
        # 删除所有相关课程.
        for course in knowledge.rel_courses.all():
            
            #ourse.delete()
            deleteTagNode(self.user, course)
        # 把与这个knowledge相关的所有节点和root相连.防止删除之后不再连通.
        for rel_know in find_all_knowledge_from_knowledge(knowledge):
            self.root.rel_knowledge.connect(rel_know)
        uid = knowledge.uid
        # knowledge.delete()
        deleteTagNode(self.user, knowledge)
        return uid
    
    def delete_node_via_uid(self, know_uid:str):
        '''
        返回被删除的节点的uid，就是know_uid.
        '''
        target = None
        for know in self.knowledges:
            if know.uid == know_uid:
                target = know
                break
        if target is None:
            raise "KnowledgeBlock does not exist in this graph"
        return self.delete_node(target, False)
    
    def deleteSelf(self):
        for i in self.knowledges:
            self.delete_node(i, False)
        uid = self.root.uid
        self.user.usergraphs_set.get(root_uid = uid).delete()
        deleteTagNode(self.user, self.root)
    
    def link_nodes(self, source:KnowledgeBlock, target:KnowledgeBlock, validate:bool = True):
        if validate:
            valid = 0
            for know in self.knowledges:
                if know == source or know == target:
                    valid += 1
                if valid == 2:
                    break
            if valid != 2:
                raise "DontExistError"
        source.rel_knowledge.connect(target)
        if self.root.rel_knowledge.is_connected(target):
            self.root.rel_knowledge.disconnect(target)

    def link_nodes_via_uid(self, source:str, target:str):
        s = None
        t = None
        for know in self.knowledges:
            if know.uid == source:
                s = know
            elif know.uid == target:
                t = know
        if s is None or t is None:
            raise "DnotExistError"
        self.link_nodes(s, t, False)