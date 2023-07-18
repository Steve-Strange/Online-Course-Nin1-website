from User.models import UserProfile, UserGraphs, UserTags
from Neo4j.models import TagNode, KnowledgeBlock, GraphRoot, Course

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


def find_all_graphs(user:UserProfile):
     '''
     寻找这个用户所拥有的所有知识图谱，返回：  
     GraphRoot的列表.
     没有进行排序，返回的就是表中的顺序——不知表中顺序是否是默认按照创建时间来的?
     '''
     return [GraphRoot.nodes.get(uid = i.root_uid) for i in user.usergraphs_set.all()]