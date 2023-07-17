from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class UserProfile(AbstractUser):
    '''
    graph_roots是一个存所有neo4j root节点编号的bytes数组.  
    以二进制而非字符形式存储，bytes为单位.  
    如果如果编号过长，在数字前后加上-1(0xff), 大端法，最左边的字节为最高位.  
    '''
    # 头像.
    profile_picture = models.ImageField(
        verbose_name="ProfilePic",
        null=True,
        blank=True,
        upload_to="image",
        max_length=200,
        default="image/default.jpg"
    )


'''
用一对多完成类似数组的效果.  
'''
class UserGraphs(models.Model):
    '''
    用户拥有的图的uid, 这个uid是string.  
    用一对多的关系来实现变长数组的效果.  
    '''
    root_uid = models.CharField(max_length=200)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    # 不指定，反向查询名字默认为 user_set