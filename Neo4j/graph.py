'''
Neo4j Graph类，包含一些操作.
'''
import json
from django.conf import settings
from os.path import join

from Neo4j.models import GraphRoot, KnowledgeBlock, Course, TagEdge
from Utils.file_operators import csv_loader, DisjointSets
from Utils.find import find_all_knowledge_in_graph, find_all_courses_in_knowledge
from User.models import UserProfile, UserGraphs, UserTags


class Graph:
    '''
    对完整的图进行操作，包括导入导出、创建等.
    '''
    def __init__(self, user:UserProfile, root:GraphRoot = None) -> None:
        '''
        指定图的根，或者不指定表示空图，将要进行创建等操作.
        '''
        self.user = user
        self.root = root
        self.knowledges = find_all_knowledge_in_graph(self.root) if self.root is not None else [KnowledgeBlock]
        self.courses = [Course]
    
    def import_json(self,json_file:str):
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
        knows = jf["knowledges"]
        edges = jf["edges"]
        courses = jf.get("courses", None)
        self.knowledges = [KnowledgeBlock]
        self.courses = [Course]
        tag_edge = [TagEdge]
        for know in knows:
            # 根据后面对数据库的更改相应添加.
            node = KnowledgeBlock(name=know["name"], introduction=know["introduction"], tag=know["tag"])
            self.knowledges.append(node)
        ds = DisjointSets(self.knowledges)
        for edge in edges:
            from_node = edge["from"]
            to_node = edge["to"]
            rel = self.knowledges[from_node].rel_knowledge.connect(self.knowledges[to_node])
            rel.tag = edge["tag"]
            if rel.tag:
                tag_edge.append(rel)
            ds.union(self.knowledges[to_node], self.knowledges[from_node])
        if courses is not None:
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
                )
                self.knowledges[course["knowledge"]].rel_courses.connect(node)
                self.courses.append(node)
        else:
            # TODO, 爬取课程.
            pass

        # 能到这一步说明较为正常.保存.
        for i in self.knowledges:
            i.save()
            if i.tag:
                UserTags(tag_uid = i.uid, user = self.user).save()
        for i in self.courses:
            i.save()
            if i.tag:
                UserTags(tag_uid = i.uid, user=self.user).save()
        for rel in tag_edge:
            UserTags(tag_uid = rel.tag, user = self.user).save()
        # TODO: 给边加tag!
        # 注册给用户.
        self.root = GraphRoot()
        graph_name = jf.get("name", None)
        if graph_name is not None:
            self.root.graph_name = graph_name
        self.root.save()
        for i in ds.get_roots():
            self.root.rel_knowledge.connect(i)
        UserGraphs(root_uid = self.root.uid, user = self.user).save()
        # 结束.

    def export_json(self, save_to_file:bool=True):
        '''
        将该图导出为json文件.保存到固定目录，文件名为graph的uid.json  
        如果save_to_file为false，就只返回字典.如果是True, 返回导出的json文件路径.
        '''
        knows_dicts = [dict]
        edges_dicts = [dict]
        courses_dicts = [dict]
        knows = find_all_knowledge_in_graph(self.root)
        for i in range(len(knows)):
            knows_dicts.append({
                "name":knows[i].name,
                "tag":knows[i].tag,
                "introduction":knows[i].introduction,
            })
            for relknow in knows[i].rel_knowledge.all():
                rel = knows[i].rel_knowledge.relationship(relknow)
                edges_dicts.append({
                    "from":i,
                    "to":knows.index(relknow),
                    "tag":rel.tag,
                })
            for course in find_all_courses_in_knowledge(knows[i]):
                courses_dicts.append({
                    "knowledge":i,
                    "tag":course.tag,
                    "name" : course.name,
                    "web" : course.web,
                    "source" : course.source,
                    "duration" : course.duration,
                    "viewer_num" : course.viewer_num,
                    "introduction" : course.introduction,
                })
        
        ret = {
            "name":self.root.graph_name,
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