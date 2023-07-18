from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from User.models import UserProfile, UserGraphs, UserTags

class UserGraphInline(admin.TabularInline):
    model = UserGraphs

class UserTagInline(admin.TabularInline):
    model = UserTags

class MyUserAdmin(UserAdmin):
    inlines = [UserGraphInline, UserTagInline]
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Picture', {'fields':('profile_picture',)}),
    )
    

# Register your models here.
admin.site.register(UserProfile, MyUserAdmin)