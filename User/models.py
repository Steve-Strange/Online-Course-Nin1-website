from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class UserProfile(AbstractUser):
    '''
    graph_roots是一个存所有neo4j root节点编号的bytes数组.  
    以二进制而非字符形式存储，bytes为单位.  
    如果如果编号过长，在数字前后加上-1(0xff), 大端法，最左边的字节为最高位.  
    '''
    graph_roots = models.BinaryField(verbose_name="GraphsRoot", editable=True)  # 暂时只放这个，后面可以加些头像什么的..?
    pass
    # TODO: 可以考虑进程binaryfield重载__str__来让admin里的输出好看点.