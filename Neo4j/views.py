from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpRequest, QueryDict, JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from Neo4j.models import TagNode, KnowledgeBlock, GraphRoot, Course
from Neo4j.graph import Graph
from Neo4j.node_operator import *
from User.models import UserProfile, UserGraphs
from Utils.find import find_all_knowledge_in_graph
from WebCrawler.crawler import crawl_courses, SourceList

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
            t = request.POST.get('submitType')
            if t == "addNode":
                # 添加节点. 这个靠底下重刷表单.
                name = request.POST.get("name")
                intro = request.POST.get("introduction")
                if name:
                    # name非空.
                    graph.create_node(name, intro)  #已经添加了,并且记录在这个类中.
            # 其它可能的输入类型...
            elif t == "linkNode":
                uid1 = request.POST.get("uid1")
                uid2 = request.POST.get("uid2")
                try:
                    graph.link_nodes_via_uid(uid1, uid2)
                except Exception as e:
                    return HttpResponse(e)
                return HttpResponse("successed")
            elif t == "download":
                d = graph.export_json(False, False)
                return JsonResponse(d)

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
            return HttpResponse("successed")

        node_datas_str, edge_datas_str = graph.get_str()
        ctx = {
            "graph":graph_root,
            "node_datas":node_datas_str,
            "edge_datas":edge_datas_str,
        }
        return render(request, "Neo4j/kgviewer.html", ctx)
    

    @login_required
    def CoursesViewer(request:HttpRequest, graph_uid:str, knowledge_uid:str):
        if not Graph.validate(request.user, graph_uid):
            return redirect(reverse("User:home"))
        try:
            know = KnowledgeBlock.nodes.get(uid = knowledge_uid)
        except:
            return redirect(reverse("Neo4j:kgviewer",kwargs={"uid":graph_uid}))
        
        src = "BiliBili"
        order = "名称"
        if request.method == "POST":
            t = request.POST.get("submitType")
            if t == "modifyFavor":
                uid = request.POST.get("uid")
                course = Course.nodes.get(uid = uid)
                modifyFavor(request.user, course)
                return HttpResponse("successed")
            else:
                src = request.POST.get("source")
                order = request.POST.get("order")
                if t == "modifyTag":
                    # 修改知识节点的tag.
                    tag = request.POST.get("tag")
                    modifyTag(request.user, know, tag)
                elif t == "modifyIntro":
                    # 修改知识节点的简介.
                    intro = request.POST.get("introduction")
                    know.introduction = intro
                    know.save()
                elif t == "crawlCourse":
                    Graph.crawlCoursesForKnowledge(know, src)
            
        # filter课程.
        if src != "Favor":
            courseList = know.rel_courses.filter(source = src)
        else:
            courseList = know.rel_courses.filter(favor = True)
        if order == "名称":
            courseList.order_by('name')
        elif order == "评分":
            courseList.order_by('-score')
        elif order == "播放量":
            courseList.order_by('-viewer_num')
        elif order == "评论数":
            courseList.order_by('-comments_num')
        elif order == "时长":
            courseList.order_by('duration')
        elif order == "更新时间":
            courseList.order_by('-time_start')
        
        ctx = {
            "know": know,
            "courseList":courseList,
            "source":src,
            "order":order,
        }
        return render(request, "Neo4j/courseList.html", ctx)