'''
加载csv格式的知识图谱。  
规定：每一行的第一个元素为该节点的知识点名称，后面全都是由这个知识点指向的其它知识点.  
不爬取课程数据.  
这个操作会创建一个新的知识图谱，包含一个root.
'''
if __name__=='__main__':
    # 在本文件上运行.
    from ..Neo4j.models import GraphRoot, KnowledgeBlock
    from neomodel import config
    config.DATABASE_URL = 'bolt://neo4j:agent-watch-orbit-anatomy-biology-7138@localhost:7687/course-recom'  
    config.MAX_CONNECTION_POOL_SIZE = 50
    config.AUTO_INSTALL_LABELS = False
    config.ENCRYPTED = False  # Neo4j默认不 Encrypted.
    config.FORCE_TIMEZONE = False  

else:
    # 不是直接在本文件上运行.
    from Neo4j.models import GraphRoot, KnowledgeBlock

def csv_loader():
    '''
    将csv文件加载为新的知识图谱。认为每行的第一个元素是该节点的课程名称，每行后面的元素是该节点指向的其它课程节点名称.
    认为不包含课程。  
    para: 
    file: 一个文件对象或者文件名称.  
    return:
    
    '''
    pass