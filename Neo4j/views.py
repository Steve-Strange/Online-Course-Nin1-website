from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from Neo4j.models import TagNode, KnowledgeBlock, GraphRoot, Course
from User.models import UserProfile, UserGraphs
from Utils.find import find_all_knowledge_in_graph

# Create your views here.

class KnowledgeGraph:
    @login_required
    def KnowledgegraphViewer(request:HttpRequest, uid:str):
        # 一定是GET!
        if request.method=='GET':
            try:
                tmp = request.user.usergraphs_set.get(root_uid = uid)
            except:
                # 该用户没有所查询的这个图!
                # TODO: 在这里跳出个模态框会比较好?
                return redirect(reverse("User:home"))  # 查询的图和用户不匹配，返回主页面.
            graph_root = GraphRoot.nodes.get(uid = uid)
            knowledges = find_all_knowledge_in_graph(graph_root)
            ctx = {
                "Knowledge_List":knowledges,
                "User":request.user,
            }
            return render(request, "Neo4j/kgviewer.html", ctx)
        else:
            return HttpResponse("不应该有除了GET之外的请求.")