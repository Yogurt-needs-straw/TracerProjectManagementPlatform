import collections

from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render

from web import models


def statistics(request, project_id):
    ''' 统计页面 '''
    return render(request, 'statistics/statistics.html')


def statistics_priority(request, project_id):
    ''' 按优先级生成饼图 '''

    # 找到所有的问题，根据优先级分组，每个优先级的问题数量
    start = request.GET.get('start')
    end = request.GET.get('end')

    # 1.构造字典
    data_dict = collections.OrderedDict()
    for key,text in models.Issues.priority_choices:
        data_dict[key] = {'name': text, 'y': 0}

    # 2.去数据库查询所有分组得到数据量
    result = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start,
                                          create_datetime__lt=end).values('priority').annotate(ct=Count('id'))

    # 3.把分组得到的数据更新到data_dict中
    for item in result:
        data_dict[item['priority']]['y'] = item['ct']

    return JsonResponse({'status': True, 'data': list(data_dict.values())})


def statistics_project_user(request):
    ''' 项目成员每个人被分配的任务数量（问题类型的配比） '''

    # 1.找到所有的问题并且需要根据指派的用户，分组。
    all_user_dict = {

    }

    context = {
        'status': True,
        'data': {
            'categories': ['1','2'],
            'series': [{
                'name': '新建',
                'data': [1,2,3]
            }]
        }
    }

    return JsonResponse(context)

