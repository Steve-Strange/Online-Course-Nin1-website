from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpRequest, QueryDict
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
        if not Graph.validate(request.user, uid):
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

        # 删除节点
        if request.method=="DELETE":
            # 要删除知识节点.
            params = QueryDict(request.body)
            know_uid = params['uid']
            print(know_uid)
            try:
                graph.delete_node_via_uid(know_uid)
            except:
                return HttpResponse("failed. this knowledge doesn't belong to the graph")
            return HttpResponse("successfully delete")

        node_datas_str, edge_datas_str = graph.get_str()
        ctx = {
            "graph":graph_root,
            "node_datas":node_datas_str,
            "edge_datas":edge_datas_str,
        }
        return render(request, "Neo4j/kgviewer.html", ctx)
    
    @login_required
    def DeleteKnowledgeNode(request:HttpRequest, graph_uid:str, knowledge_uid:str):
        if not Graph.validate(request.user, graph_uid):
            return redirect(reverse("User:home"))
        graph_root = GraphRoot.nodes.get(uid = graph_uid)
        graph = Graph(request.user, graph_root)
        try:
            graph.delete_node_via_uid(knowledge_uid)
        except:
            return redirect(reverse("Neo4j:kgviewer", kwargs={"uid":graph_uid,}))
        # 不管成不成功都直接返回...
        return redirect(reverse("Neo4j:kgviewer", kwargs={"uid":graph_uid,}))