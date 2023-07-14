from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from User.models import UserProfile

class MyUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Knowledge Roots Array (binary)', {'fields':('graph_roots',)}),
    )
    

# Register your models here.
admin.site.register(UserProfile, MyUserAdmin)