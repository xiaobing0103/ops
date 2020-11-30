from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Server(models.Model):
    productid = models.CharField(unique=True,max_length=20)
    brand = models.CharField(max_length=20)
    servername = models.CharField(max_length=50)
    model = models.CharField(max_length=50)    
    status = models.CharField(max_length=20)
    cpu_model = models.CharField(null=True,blank=True,max_length=50)
    cpu_quantity = models.CharField(max_length=10)
    cpu_core = models.CharField(max_length=10)
    memory_quantity = models.CharField(max_length=10)
    memory_total = models.CharField(max_length=10)
    ssd_quantity = models.CharField(blank=True,null=True,max_length=10)
    ssd_total = models.CharField(blank=True,null=True,max_length=10)
    hdd_quantity = models.CharField(blank=True,null=True,max_length=10)
    hdd_total = models.CharField(blank=True,null=True,max_length=10)
    raid_type = models.CharField(blank=True,null=True,max_length=10)   
    idrac_ip = models.CharField(blank=True,null=True,max_length=20)
    purchase_date = models.CharField(blank=True,null=True,max_length=20)
    warranty_end = models.CharField(blank=True,null=True,max_length=20)   
    function = models.CharField(blank=True,null=True,max_length=50)
    data_center = models.CharField(max_length=20)
    network = models.CharField(blank=True,null=True,max_length=100)
    idrac_network = models.CharField(blank=True,null=True,max_length=100)
    rack = models.CharField(max_length=10)
    rack_u = models.CharField(max_length=10)

class Os(models.Model):
    productid = models.CharField(blank=True,null=True,max_length=20)
    server_type = models.CharField(blank=True,null=True,max_length=10)
    hostname = models.CharField(blank=True,null=True,max_length=50)
    system_version = models.CharField(blank=True,null=True,max_length=50)    
    status = models.CharField(blank=True,null=True,max_length=10)
    kernel = models.CharField(null=True,blank=True,max_length=50)
    core_quantity = models.CharField(blank=True,null=True,max_length=10)
    memory = models.CharField(blank=True,null=True,max_length=10)
    hdd = models.CharField(blank=True,null=True,max_length=10)
    vlan = models.CharField(blank=True,null=True,max_length=10)
    ip = models.CharField(unique=True,max_length=20)
    esxi_ip = models.CharField(blank=True,null=True,max_length=20)
    zbx_stau = models.CharField(blank=True,null=True,max_length=20)
    application = models.CharField(blank=True,null=True,max_length=100)
    administrator = models.CharField(blank=True,null=True,max_length=50)
    remarks = models.CharField(blank=True,null=True,max_length=100)

class Doc(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    text = models.TextField()
    author = models.CharField(max_length=20)
    createtime = models.CharField(max_length=20)
    editortime = models.CharField(blank=True,null=True,max_length=20)

class Cmanage(models.Model):
    title = models.CharField(max_length=50) 
    content = models.TextField()
    effect = models.CharField(max_length=100)
    rollback = models.CharField(max_length=100)
    statu = models.CharField(max_length=10)
    author = models.CharField(max_length=20)
    cdate = models.DateField(auto_now_add=True)        #工单创建日期
    ctime = models.CharField(max_length=20)            #工单创建时间
    witime = models.CharField(max_length=50)           #变更窗口时间
    end_time = models.CharField(max_length=20)         #实际变更结束时间
    reviewer = models.CharField(max_length=20)         #核查人
    confirm = models.CharField(max_length=100)         #

class Directory(models.Model):
    dirname = models.CharField(max_length=50)
    grade = models.IntegerField()
    parentid = models.IntegerField()
    class Meta:
        unique_together=('dirname','grade')

class Document(models.Model):
    filename = models.CharField(max_length=50)
    filepath = models.CharField(max_length=50)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    createtime = models.CharField(max_length=20)
    editortime = models.CharField(blank=True,null=True,max_length=20)
    class Meta:
        unique_together=('directory','filename')

class Progroup(models.Model):
    group = models.CharField(max_length=20)                         #用户组名称

class Usergroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Progroup, on_delete=models.CASCADE)
    label = models.IntegerField()                                   #0成员，1属主

class Properm(models.Model):
    project = models.ForeignKey(Directory, on_delete=models.CASCADE)            #项目id                     
    group = models.ForeignKey(Progroup, on_delete=models.CASCADE)               #用户组id
    perm = models.CharField(max_length=5)                                       #view查看，edit编辑，owner属主

class Personal(models.Model):
    project = models.ForeignKey(Directory, on_delete=models.CASCADE)            #项目id
    user = models.ForeignKey(User, on_delete=models.CASCADE)                    #用户id