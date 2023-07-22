'''
Neo4j Graph类，包含一些操作.
'''
from neomodel import db
import json
from jsonschema import validate, draft7_format_checker
from django.conf import settings
from os.path import join

from Neo4j.models import GraphRoot, KnowledgeBlock, Course, TagEdge
from Utils.file_operators import csv_loader, DisjointSets
from Utils.find import find_all_knowledge_in_graph, find_all_courses_in_knowledge
from User.models import UserProfile, UserGraphs, UserTags


class Graph:
    with open("static/graphs/schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)
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
        validate(instance=jf, schema=Graph.schema, format_checker=draft7_format_checker)
        # 如果验证失败会直接抛出异常.
        # 通过了之后能直接进行下面的语句.
        knows = jf["knowledges"]
        edges = jf["edges"]
        courses = jf["courses"]
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
                ).save()
                self.knowledges[course["knowledge"]].rel_courses.connect(node)
                if node.tag:
                    UserTags(tag_uid = node.uid, user = self.user).save()
        else:
            # TODO, 爬取课程.
            pass

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

    
    @db.read_transaction
    def export_json(self, save_to_file:bool=True, get_tag:bool = False):
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
                "tag":knows[i].tag if get_tag else "",
                "introduction":knows[i].introduction,
            })
            for relknow in knows[i].rel_knowledge.all():
                rel = knows[i].rel_knowledge.relationship(relknow)
                edges_dicts.append({
                    "from":i,
                    "to":knows.index(relknow),
                    "tag":rel.tag if get_tag else "",
                })
            for course in find_all_courses_in_knowledge(knows[i]):
                courses_dicts.append({
                    "knowledge":i,
                    "tag":course.tag if get_tag else "",
                    "name" : course.name,
                    "web" : course.web,
                    "source" : course.source,
                    "duration" : course.duration,
                    "viewer_num" : course.viewer_num,
                    "introduction" : course.introduction,
                })
        
        ret = {
            "name":self.root.graph_name,
            "introduction":self.root.introduction,
            "tag":self.root.tag if get_tag else "",
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