'''
此文件进行知识图谱文件的导入、导出操作.
'''


'''
加载csv格式的知识图谱。  
规定：每一行的第一个元素为该节点的知识点名称，后面全都是由这个知识点指向的其它知识点.  
不爬取课程数据.  
这个操作会创建一个新的知识图谱，包含一个root.
'''
from copy import copy
from csv import reader as csv_reader

if __name__=='__main__':
    # 在本文件上运行.
    from ..Neo4j.models import GraphRoot, KnowledgeBlock, placeholder
    from neomodel import config
    config.DATABASE_URL = 'bolt://neo4j:agent-watch-orbit-anatomy-biology-7138@localhost:7687/course-recom'  
    config.MAX_CONNECTION_POOL_SIZE = 50
    config.AUTO_INSTALL_LABELS = False
    config.ENCRYPTED = False  # Neo4j默认不 Encrypted.
    config.FORCE_TIMEZONE = False  

else:
    # 不是直接在本文件上运行.
    from Neo4j.models import GraphRoot, KnowledgeBlock, placeholder


class DisjointSets:
    def __init__(self, init_set:list) -> None:
        '''
        需要给定初始的不相交集，即所有节点的列表或元组.需保证无重复.
        init_set指定之后应该不能再修改!
        '''
        self.elem = init_set
        self.sets = [-1 for i in range(len(init_set))]  #-1表示为根.
    
    def get_id(self, obj):
        '''
        返回obj在这个数据结构中的id, 如果不存在则返回None.
        '''
        try:
            id = self.elem.index(obj)
        except:
            return None  # 不存在.
        return id
    
    def find(self, obj):
        '''
        找到obj所在的集合的根.
        '''
        id = self.get_id(obj)
        if id is None:
            return None
        while self.sets[id] != -1:
            id = self.sets[id]
        return self.elem[id]
    
    def union(self, obj1, obj2):
        '''
        将obj1, obj2 所在的集合合并，返回新集合的根.
        直接把obj2的各的父亲置为obj1, 以求简单.
        '''
        id1 = self.get_id(obj1)
        id2 = self.get_id(obj2)
        if id1 is None or id2 is None:
            return None
        while self.sets[id1] != -1:
            id1 = self.sets[id1]
        while self.sets[id2] != -1:
            id2 = self.sets[id2]
        if id1==id2:
            return self.elem[id1]  # 本来就在同一个集合.
        self.sets[id2] = id1       # 右边合并到左边.
        return self.elem[id1]
    
    def get_roots(self):
        '''
        获取所有不相交集合的根。
        '''
        ret = []
        for i in range(len(self.elem)):
            if self.sets[i] == -1:
                ret.append(self.elem[i])
        return ret


def csv_loader(file, name:str = None, intro:str = None):
    '''
    这个函数是错误的！弃用！
    只用json吧！

    将csv文件加载为新的知识图谱。认为每行的第一个元素是该节点的课程名称，每行后面的元素是该节点指向的其它课程节点名称.
    认为不包含课程。这个函数也不会去爬取课程，形成的图是没有课程的.  
    注意，这里只做加载，**不做爬取**！
    para: 
    file: 一个文件对象或者文件名称.  
    name: 这张图的名字.
    return:
    root(GraphRoot)本身.
 
    '''
    # 因为neomodel支持双向查询，只需要弱连通分支即可.
    # 使用并查集，让GraphRoot指向每一个弱连通分支中的任一个节点.
    should_close = False
    if type(file)==str:
        f = open(file, 'r', encoding='utf-8')
        should_close = True
    else:
        f = file
    root = GraphRoot()
    if name is not None:
        root.graph_name = name
    if intro is not None:
        root.introduction = intro
    root.save()
    reader = csv_reader(f)
    node_dict = {str:KnowledgeBlock}
    # 先遍历一遍创建所有节点.
    for row in reader:
        for raw_name in row:
            name = raw_name.strip()
            if node_dict.get(name, None) is None:
                # 是新节点，要创建.
                node = KnowledgeBlock(name = name).save()
                node_dict[name] = node
    # 再次遍历，进行连接，并且进行并查集操作.
    ds = DisjointSets(list(node_dict.values()))            
    for row in reader:
        # 第一个是该节点的name(可能重复), 后面的全都是这个节点指向其它节点.
        thisnode_name = row[0].strip()
        thisnode = node_dict[thisnode_name]  #一定有效.
        for i in range(1, len(row)):
            relnode_name = row[i].strip()
            relnode = node_dict[relnode_name]
            ds.union(thisnode, relnode)
            thisnode.rel_knowledge.connect(relnode)
    # 获取所有弱连通分支.并将其和root相连.
    for branch in ds.get_roots():
        root.rel_knowledge.connect(branch)

    if should_close:
        f.close()

    return root
