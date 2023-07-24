from neomodel import Traversal
from neomodel.match import EITHER, OUTGOING
from neomodel import db
from User.models import UserProfile, UserGraphs, UserTags
from Neo4j.models import TagNode, KnowledgeBlock, GraphRoot, Course, TagEdge

@db.read_transaction
def find_all_tags(user : UserProfile):
        '''
        找到这个User的所有有tag的节点。返回：  
        {
            "GraphTags": []
            "KnowTags": []
            "CourseTags": []
        }
        '''
        ret = {
            "GraphTags" : [],
            "KnowTags":   [],
            "CourseTags": [],
        }
        tag_node = user.usertags_set.all()
        for i in tag_node:
            uid = i.tag_uid
            node = TagNode.nodes.get(uid = uid)
            if isinstance(node, GraphRoot):
                ret["GraphTags"].append(node)
            elif isinstance(node, KnowledgeBlock):
                ret["KnowTags"].append(node)
            else:
                ret["CourseTags"].append(node)
        
        return ret


@db.read_transaction
def find_all_graphs(user:UserProfile):
    '''
    寻找这个用户所拥有的所有知识图谱，返回：  
    GraphRoot的列表.
    没有进行排序，返回的就是表中的顺序——不知表中顺序是否是默认按照创建时间来的?
    '''
    return [GraphRoot.nodes.get(uid = i.root_uid) for i in user.usergraphs_set.all()]


@db.read_transaction
def find_all_knowledge_from_knowledge(source:KnowledgeBlock, dual_direction:bool = True, lazy:bool = False):
    '''
    以souce为中心，找到所有与source直接相连的KnowledgeBlock节点.  
    dual_direction: 是否双向查询，默认是。如是，则将边当成无向边.如否，只返回source所指向的节点.
    lazy: 默认否。如是，则获取的节点只有id, 不获取其它成员变量值以加速.
    '''
    definition = dict(
        node_class = KnowledgeBlock,
        direction = EITHER if dual_direction else OUTGOING,
        relation_type = None,
        model = TagEdge,
    )
    traversal = Traversal(source, KnowledgeBlock.__label__, definition)
    return traversal.all(lazy)


@db.read_transaction
def find_all_knowledge_in_graph(root : GraphRoot):
    '''
    使用BFS找到root指向的所有知识点节点.只返回知识点节点!  
    返回：一个列表，里面是这个图中的所有知识点节点，暂时没有顺序要求，按照之后可视化的要求改！  
    return: list[KnowledgeBlock]
    '''
    # 注意，必须把边当成无向边来处理，否则可能会有遗漏!  
    ret = []
    queue = []  # for BFS.
    for branch in root.rel_knowledge.all():
        # branch是每个分支中的一个节点.
        queue.append(branch)
        while len(queue) > 0:
            curnode = queue.pop(0)
            ret.append(curnode)
            # 一步BFS.找与它直接相连的点(方向随意).
            definition = dict(
                 node_class = KnowledgeBlock,
                 direction = EITHER,
                 #relation_type = KnowledgeBlock.rel_knowledge,
                 relation_type = None,
                 model = TagEdge,
            )   # 定义双向Traversal.
            dual_traversal = Traversal(curnode, KnowledgeBlock.__label__, definition)
            next_nodes = dual_traversal.all()
            for node in next_nodes:
                if node in ret or node in queue:
                    continue
                queue.append(node)
    return ret


@db.read_transaction
def find_all_courses_in_knowledge(knowledge:KnowledgeBlock):
    '''
    找到一个知识点节点的所有课程节点，返回一个列表[Course]
    '''
    return knowledge.rel_courses.all()