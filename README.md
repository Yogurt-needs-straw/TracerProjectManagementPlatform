# Django-TracerProjectManagementPlatform

这个是一个项目管理平台

##### 1.完成用户管理

##### 2.星标

> 思路：在获取项目列表的同时，将用户创建项目以及参与项目，使用字典进行封装。
>
> value:表示项目信息
>
> type:表示项目类型

需注意使用path方法类型转化器

```python
path('test/<int:year>/', views.year_test),
Django 提供了自定义转换器。下面介绍 Django 默认支持的转换器，如下所示：
str，匹配除了路径分隔符（/）之外的非空字符串，这是默认的形式；
int，匹配正整数，包含0；
slug，匹配字母、数字以及横杠、下划线组成的字符串；
uuid，匹配格式化的 uuid，如 075194d3-6885-417e-a8a8-6c931e272f00；
path，匹配任何非空字符串，包含了路径分隔符。
```

2.1添加星标（项目收藏、特别关注）

```
我创建的项目：Project的star=True
我参与的项目：ProjectUser的star=True
```

2.2移除星标

```
我创建的项目：Project的star=False
我参与的项目：ProjectUser的star=False
```



##### 3.选择颜色

> 思路：1.排除默认添加的color插件，不添加form-control  2.不使用模板中的select radio标签。3.构建新的radio标签。4.隐藏radio选项，将色块显现，用css对色块形状进行修改。

3.1 **部分样式应用BootStrapForm**

```python
class BootStrapForm(object):

    bootstrap_class_exclude = []

    # 样式重写
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # 排除color选项 不添加 form-control
            if name in self.bootstrap_class_exclude:
                continue

            # 给所有标签添加class属性 form-control
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)

```

```python
class ProjectModelForm(BootStrapForm, forms.ModelForm):
    # 排除color插件 不添加 form-control  
    bootstrap_class_exclude = ['color']  # 排除默认添加

    class Meta:
		model = model.Project
        fields = "__all__"
```



3.2**定制ModelForm的插件**

```python
class ProjectModelForm(BootStrapForm, forms.ModelForm):
    
    class Meta:
        model = models.Project
        fields = "__all__"
        # 重写插件属性
        widgets = {
            'desc': forms.Textarea,
            'color': ColorRadioSelect(attrs={'class': 'color-radio'}),
        }
```

```python
from django.forms import RadioSelect


class ColorRadioSelect(RadioSelect):

    # template_name = 'django/forms/widgets/checkbox_select.html'
    # option_template_name = 'django/forms/widgets/checkbox_option.html'

    template_name = 'widgets/color_radio/radio.html'
    option_template_name = 'widgets/color_radio/radio_option.html'
```

template_name = 'widgets/color_radio/radio.html'

```django
{% with id=widget.attrs.id %}
    <div{% if id %} id="{{ id }}"{% endif %}{% if widget.attrs.class %} class="{{ widget.attrs.class }}"{% endif %}>
        {% for group, options, index in widget.optgroups %}
            {% for option in options %}
                <label {% if option.attrs.id %} for="{{ option.attrs.id }}"{% endif %} >
                    {% include option.template_name with widget=option %}
                </label>
            {% endfor %}
        {% endfor %}
    </div>
{% endwith %}

```

​    option_template_name = 'widgets/color_radio/radio_option.html'

```django
{% include "django/forms/widgets/input.html" %}
<span class="cycle" style="background-color:{{ option.label }}"></span>
```



3.3 **项目选择颜色**

3.1、3.2 知识点的应用 + 前端样式的编写



##### 4.切换菜单

> 思路：使用@register.inclusion_tag 装饰器 将切换菜单嵌入到 manage 模板文件中

```python
1.数据库中获取
	我创建的：
    我参与的：
2.循环显示
3.当前页面需要显示 / 其他页面也需要显示 [inclusion_tap]
```

```python
@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
    ''' 菜单栏项目列表 '''
    # 1.获取创建的所有项目
    my_project_list = models.Project.objects.filter(creator=request.tracer.user)

    # 2.获取参与的所有项目
    join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)

    return {"my": my_project_list, "join": join_project_list}
```



all_project_list.html

```html
<ul class="dropdown-menu">
    {# 判断是否有值 决定是否显示 #}

    {% if my %}
    {# 创建的项目   #}
    <li><i class="fa fa-list" aria-hidden="true"></i> 我创建的项目</li>
      {% for item in my %}
        <li><a href="#">{{ item.name }}</a></li>
      {% endfor %}
    <li role="separator" class="divider"></li>
    {% endif %}

    {% if join %}
    {# 参与的项目   #}
      <li><i class="fa fa-handshake-o" aria-hidden="true"></i> 我参与的项目</li>
      {% for item in join %}
        <li><a href="#">{{ item.project.name }}</a></li>
      {% endfor %}
    <li role="separator" class="divider"></li>
    {% endif %}

      <li><a href="/project/list">所有项目</a></li>
  </ul>
```



##### 5.项目管理

> 思路：项目路由
>
> /manage/[项目id]/dashboard
>
> /manage/[项目id]/issues
>
> /manage/[项目id]/statistics
>
> /manage/[项目id]/file
>
> /manage/[项目id]/wiki
>
> /manage/[项目id]/setting

路由设计

```python
    # 进入项目管理
    # 使用路由分发
    path('manage/<int:project_id>/', include([
        path('dashboard/', manage.project_dashboard, name='project_dashboard'),
        path('issues/', manage.project_issues, name='project_issues'),
        path('statistics/', manage.project_statistics, name='project_statistics'),
        path('file/', manage.project_file, name='project_file'),
        path('wiki/', manage.project_wiki, name='project_wiki'),
        path('setting/', manage.project_setting, name='project_setting'),
    ], None)),
```

##### 5.1 进入项目展示菜单

```
- 进入项目
- 展示菜单
```

**5.1.1 是否已经进入项目？**【中间件】

判断URL是否是manage开头

project_id 判断 是否是该用户的 是什么类型的项目

**5.1.2 显示菜单**

依赖：是否已经进入项目？

```html
通过 request.tracer.project 判断
<ul class="nav navbar-nav">
      <li><a href="#">概述</a></li>
      <li><a href="#">wiki</a></li>
</ul>
```

**5.1.3 页面样式调整**

去掉 all_project_list 模板中的 `<ul class="nav navbar-nav">` ，在manage.html中添加`<ul>`标签，将项目菜单栏合为一个`<ul>`

**5.1.4 项目菜单默认选中**

> 思路：使用 inclusion_tag 实现项目切换

注意 django.urls 中的 reverse 用法 reverse("[app_name]:[urlname]")

```python
@register.inclusion_tag('inclusion/manage_menu_list.html')
def manage_menu_list(request):
    data_list = [
        {'title': '概览', 'url': reverse("web:dashboard", kwargs={'project_id': request.tracer.project.id})},
        {'title': '问题', 'url': reverse('web:issues', kwargs={'project_id': request.tracer.project.id})},
        {'title': '统计', 'url': reverse('web:statistics', kwargs={'project_id': request.tracer.project.id})},
        {'title': 'wiki', 'url': reverse('web:wiki', kwargs={'project_id': request.tracer.project.id})},
        {'title': '文件', 'url': reverse('web:file', kwargs={'project_id': request.tracer.project.id})},
        {'title': '配置', 'url': reverse('web:setting', kwargs={'project_id': request.tracer.project.id})},
    ]

    return {'data_list': data_list}
```

#### 6 wiki

- 表结构设计
- 快速开发
- 应用markdown组件
- 腾讯COS做上传

##### 6.1 表结构设计

| ID   | 标题 | 内容 | 项目ID | 父ID |
| ---- | ---- | ---- | ------ | ---- |
| 1    | xx   | xxxx | 1      | null |
| 2    | xx   | xxxx | 2      | 1    |
| 3    |      |      | 3      | 1    |

**models.py**

```python
class Wiki(models.Model):
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='标题', max_length=32)
    content = models.TextField(verbose_name='内容')

    # 子关联  related_name 反向关联字段
    parent = models.ForeignKey(verbose_name='父文章', to='Wiki', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
```

**注意1：**

设置字段时，使用to时，在定义外键的时候加上"on_delete=“；

> 原因：django升级到2.0之后，表与表之间关联的时候必须写"on_delete"参数，否则会报错

例如：

```python
book = models.ForeignKey(BookInfo,on_delete=models.CASCADE)
```

扩展补充
(1)、on_delete = None：
删除关联表的数据时，当前表与关联表的filed的行为。
(2)、on_delete = models.CASCADE：
表示级联删除，当关联表（子表）中的数据删除时，与其相对应的外键（父表）中的数据也删除。
(3)、on_delete = models.DO_NOTHING:
你删你的，父亲（外键）不想管你
(4)、on_delete = models.PROTECT:
保护模式，如采用这个方法，在删除关联数据时会抛出ProtectError错误
(5)、on_delete = models.SET_DEFAULT:
设置默认值，删除子表字段时，外键字段设置为默认值，所以定义外键的时候注意加上一个默认值。
(6)、on_delete = models.SET（值）:
删除关联数据时，自定义一个值，该值只能是对应指定的实体
(7)、on_delete = models.SET_NULL
置空模式，删除时，外键字段被设置为空，前提就是blank=True, null=True,定义该字段时，允许为空。理解：删除关联数据（子表），与之关联的值设置默认值为null（父表中），这个前提需要父表中的字段可以为空。

**注意2：**

**通过主表来查询子表**

> A.objects.get(id=A_id).test.all().order_by('-created'),
>
> django 默认每个主表的对象都有一个是外键的属性，可以通过它来查询到所有属于主表的子表的信息。这个属性的名称默认是以子表的名称小写加上_set()来表示(上面默认以b_set访问)，默认返回的是一个querydict对象。
>
> related_name 可以给这个外键定义好一个别的名称

**通过子表来查询主表**

> B.objects.filter(a=A_id).order_by('-created')

**6. wiki开发流程**

