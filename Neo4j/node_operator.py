'''
加tag, 收藏课程等操作.
'''
from Neo4j.models import TagNode, Course
from User.models import UserProfile, UserFavorites, UserTags

def modifyTag(user:UserProfile, node:TagNode, newtag:str):
    '''
    修改tag，注意，如果原先tag是“”，就要注册到user里；如果新tag是空，就删除.
    '''
    if not newtag:
        # 是空, 看看需不需要删除.
        should_delete = True
        try:
            usertag = user.usertags_set.get(tag_uid = str(node.uid))
        except:
            should_delete = False  #不存在，不用注销.
        if should_delete:
            usertag.delete()
    else:
        # 不是空，看看需不需要注册.
        try:
            usertag = user.usertags_set.get(tag_uid = str(node.uid))
        except:
            # 不存在，要注册一个.
            usertag = UserTags(tag_uid = node.uid, user = user)
    # 修改node.
    node.tag = newtag
    node.save()


def modifyFavor(user:UserProfile, course:Course):
    # 直接取反.
    if course.favor:
        # 要变为False, 需要注销.
        userfavor = user.userfavorites_set.get(course_uid = course.uid)
        userfavor.delete()
        course.favor = False
    else:
        # 要变为True, 要注册到用户里.
        userfavor = UserFavorites(course_uid = course.uid, user = user).save()
        course.favor = True
    course.save()

def deleteTagNode(user:UserProfile, node:TagNode):
    # 注意要连带着删除tag, favor等.
    if isinstance(node, Course):
        if node.favor:
            f = user.userfavorites_set.get(course_uid = node.uid)
            f.delete()
    if node.tag:
        f = user.usertags_set.get(tag_uid = node.uid)
        f.delete()
    node.delete()