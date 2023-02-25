
from django.shortcuts import render
from django.http import JsonResponse

from web import models
from web.forms.file import FolderModelForm

def file(request, project_id):
    ''' 文件列表 & 添加文件夹 '''
    # 获取父级文件夹
    parent_object = None
    folder_id = request.GET.get('folder', "")  # 如果有值获取folder 如果没有值为空
    # 判断是否是十进制的值
    if folder_id.isdecimal():
        parent_object = models.FileRepository.objects.filter(id=int(folder_id), file_type=2,
                                                             project=request.tracer.project).first()
    # GET 查看页面
    if request.method == "GET":

        breadcrumb_list = []
        parent = parent_object
        while parent:
            breadcrumb_list.insert(0, {'id': parent.id, 'name': parent.name})
            parent = parent.parent

        # 当前目录下所有的文件和文件夹获取到
        queryset = models.FileRepository.objects.filter(project=request.tracer.project)
        if parent_object:
            # 进入目录
            file_object_list = queryset.filter(parent=parent_object).order_by('-file_type')
        else:
            # 跟目录
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')

        form = FolderModelForm(request, parent_object)

        context = {
            'form': form,
            "file_object_list": file_object_list,
            "breadcrumb_list": breadcrumb_list,
        }
        return render(request, 'file/file.html', context)

    # POST 添加文件夹 & 文件夹的修改
    fid = request.POST.get('fid', '')
    edit_object = None
    if fid.isdecimal():
        edit_object = models.FileRepository.objects.filter(id=int(fid), file_type=2, project=request.tracer.project).first()

    if edit_object:
        # 编辑
        form = FolderModelForm(request, parent_object, data=request.POST, instance=edit_object)
    else:
        # 添加
        form = FolderModelForm(request, parent_object, data=request.POST)

    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_object
        # 往数据库添加文件夹
        form.save()
        return JsonResponse({'status': True})


    return JsonResponse({'status': False, 'error': form.errors})


# http://127.0.0.1:8000/manage/1/file/delete/?fid=1
def file_delete(request, project_id):
    ''' 删除文件 '''

    fid = request.GET.get('fid')

    # 删除文件 & 文件夹（级联删除）
    delete_object = models.FileRepository.objects.filter(id=fid, project=request.tracer.project).first()
    if delete_object.file_type == 1:
        # 删除文件（数据库文件删除，cos文件删除，项目已使用的空间容量返还）
        pass
    else:
        # 删除文件夹（找到文件夹下所有的文件>数据库文件删除，cos文件删除，项目已使用的空间容量返还）
        pass

    delete_object.delete()
    return JsonResponse({'status': True})
