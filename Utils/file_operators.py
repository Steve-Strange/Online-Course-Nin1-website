'''
此文件进行知识图谱文件的导入、导出操作.
'''


'''
加载csv格式的知识图谱。  
规定：每一行的第一个元素为该节点的知识点名称，后面全都是由这个知识点指向的其它知识点.  
不爬取课程数据.  
这个操作会创建一个新的知识图谱，包含一个root.
'''
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

def csv_loader(file, name:str = None, intro:str = None):
    '''
    将csv文件加载为新的知识图谱。认为每行的第一个元素是该节点的课程名称，每行后面的元素是该节点指向的其它课程节点名称.
    认为不包含课程。这个函数也不会去爬取课程，形成的图是没有课程的.  
    注意，这里只做加载，**不做爬取**！
    para: 
    file: 一个文件对象或者文件名称.  
    name: 这张图的名字.
    return:
    root(GraphRoot)本身.

    TODO: (并查集)严格来说，root应该连接图里的所有分支，这里暂且做不到.  
    如果输入的图不是连通的，会出问题.  
    '''
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
    first_node = None
    node_dict = {}
    first = True
    for row in reader:
        # 第一个是该节点的name(可能重复), 后面的全都是这个节点指向其它节点.
        thisnode_name = row[0].strip()
        # 判断是否要创建这个节点.
        thisnode = node_dict.get(thisnode_name, None)
        if thisnode is None:
            # 新节点，要创建.
            thisnode = KnowledgeBlock(name = thisnode_name).save()
            node_dict[thisnode_name] = thisnode
        if first:
            first_node = thisnode
            first = False
        for i in range(1, len(row)):
            relnode_name = row[i].strip()
            relnode = node_dict.get(relnode_name, None)
            if relnode is None:
                relnode = KnowledgeBlock(name=relnode_name).save()
                node_dict[relnode_name] = relnode
            thisnode.rel_knowledge.connect(relnode)
    
    if first_node is None:
        # 是一张空表，创建一个空节点.
        first_node = KnowledgeBlock(name = placeholder).save()
    root.rel_knowledge.connect(first_node)

    if should_close:
        f.close()

    return root