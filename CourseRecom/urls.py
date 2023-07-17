"""
URL configuration for CourseRecom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(("User.urls", "User"))),  
    # 默认重定向到user里.
    # 后面那里定义了命名空间.似乎也可以在User/urls.py底下用app_name="User".  
    path('Neo4j/', include(("Neo4j.urls", "Neo4j"))),
    # 访问Neo4j下的url需要用Neo4j/...
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
