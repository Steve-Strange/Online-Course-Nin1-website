from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from Neo4j.models import TagNode, KnowledgeBlock, GraphRoot, Course
from Neo4j.graph import Graph
from User.models import UserProfile, UserGraphs
from Utils.find import find_all_knowledge_in_graph

# Create your views here.

class KnowledgeGraph:
    @login_required
    def KnowledgegraphViewer(request:HttpRequest, uid:str):
        try:
            tmp = request.user.usergraphs_set.get(root_uid = uid)
        except:
            # 该用户没有所查询的这个图.
            # TODO: 这里可能给个message比较好.
            return redirect(reverse("User:home"))
        graph_root = GraphRoot.nodes.get(uid = uid)
        graph = Graph(request.user, graph_root)
        if request.method=="POST":
            if request.POST.get('submitType') == "addNode":
                # 添加节点.
                name = request.POST.get("name")
                intro = request.POST.get("introduction")
                if name:
                    # name非空.
                    graph.create_node(name, intro)  #已经添加了,并且记录在这个类中.
            # 其它可能的输入类型...

        node_datas_str, edge_datas_str = graph.get_str()
        ctx = {
            "graph":graph_root,
            "node_datas":node_datas_str,
            "edge_datas":edge_datas_str,
        }
        return render(request, "Neo4j/kgviewer.html", ctx)