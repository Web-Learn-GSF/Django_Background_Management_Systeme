'''导入实例
1. 自定义视图函数，并获得数据列表【全部、筛选都可以】
2. 实例化Pagination对象为pagination_object，同时传入（request, data_list_selected）两个参数
3. -- pagination_object.data_list_PerPageShow   该属性可以获得每页展示的数据列表，并传入html界面
   -- pagination_object.Html_Pagination()       该函数可以生成分页展示的li标签，并传入html界面


def admin_list(request):
    choices_list = {}
    search_result = request.GET.get('search_data', '')  # 有数值取数值，没数值得到空字符串
    if search_result:
        choices_list['mobile__contains'] = search_result
        
    data_list_selected = models.Admin.objects.filter(**choices_list)    
    pagination_object = Pagination(request, data_list_selected)
    context = {
        'admin_list':pagination_object.data_list_PerPageShow,
        'search_result':search_result,
        'page_string':pagination_object.Html_Pagination()
    }
    return render(request, 'admin_list.html', context)
    
'''

from django.shortcuts import render, HttpResponse, redirect
from app01 import models
from django.utils.safestring import mark_safe
from django.http.request import QueryDict
import copy


class Pagination(object):
    """_实现页面数据分页_
        Args:
            request (_django.core.handlers.wsgi.WSGIRequest_): _请求的对象_
            data_list_selected (_django.db.models.query.QuerySet_): _符合筛选条件的数据_
            page_size (int, optional): _每页展示的数据条数_. Defaults to 15.
            page_parm (str, optional): _在URL中传递用于获取分页的参数：例：/prettynum/list/?page=7_. Defaults to 'page'.
            plus (int, optional): _显示当前页前后的页数_. Defaults to 5.
    """

    def __init__(self, request, data_list_selected, page_size=15, page_parm='page', plus=5):

        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable_ = True

        self.query_dict = query_dict
        self.page_parm = page_parm

        total_data_number = data_list_selected.count()
        self.total_page_count, div = divmod(total_data_number, page_size)
        if div:
            self.total_page_count += 1
        self.total_page_count = 1 if self.total_page_count == 0 else self.total_page_count

        page = request.GET.get(page_parm, '1')
        if page.isdecimal():
            page = int(page)
            page = 1 if page < 1 else page
            page = self.total_page_count if page > self.total_page_count else page

        else:
            page = 1
        self.page = int(page)
        self.data_start = (page - 1) * page_size
        self.data_end = page * page_size
        self.data_list_PerPageShow = data_list_selected[self.data_start:self.data_end]

        if self.total_page_count <= 2 * plus + 1:
            start_page = 1
            end_page = self.total_page_count
        else:
            if self.page <= plus + 1:
                start_page = 1
                end_page = 11

            elif plus + 1 < self.page < self.total_page_count - 5:
                start_page = self.page - plus
                end_page = self.page + plus
            elif self.total_page_count - 5 <= self.page:
                start_page = self.total_page_count - 10
                end_page = self.total_page_count
        self.start_page = start_page
        self.end_page = end_page

    def Html_Pagination(self):
        # 首页
        page_str_list = []
        self.query_dict.setlist(self.page_parm, [1])
        page_str_list.append('<li><a href="?{}">{}<span class="sr-only">(current)</span></a></li>'.format(self.query_dict.urlencode(), '首页'))

        # 上一页
        if self.page > 1:
            self.query_dict.setlist(self.page_parm, [self.page - 1])
            ele = '<li><a href="?{}" aria-label="Previous"><span aria-hidden="true">«</span></a></li>'.format(self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_parm, [1])
            ele = '<li class="disabled"><a href="?{}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.format(
                self.query_dict.urlencode())
        page_str_list.append(ele)

        for i in range(self.start_page, self.end_page + 1):
            if i == self.page:
                self.query_dict.setlist(self.page_parm, [i])
                ele = '<li class="active"><a href="?{}">{}<span class="sr-only">(current)</span></a></li>'.format(self.query_dict.urlencode(), i)
            else:
                self.query_dict.setlist(self.page_parm, [i])
                ele = '<li><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            page_str_list.append(ele)

        # 下一页
        if self.page < self.total_page_count:
            self.query_dict.setlist(self.page_parm, [self.page + 1])
            ele = '<li><a href="?{}" aria-label="Next"><span aria-hidden="true">»</span></a></li>'.format(self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_parm, [self.total_page_count])
            ele = '<li class="disabled"><a href="?{}" aria-label="Next"><span aria-hidden="true">»</span></a></li>'.format(
                self.query_dict.urlencode())
        page_str_list.append(ele)

        # 尾页
        self.query_dict.setlist(self.page_parm, [self.total_page_count])
        page_str_list.append('<li><a href="?{}">{}<span class="sr-only">(current)</span></a></li>'.format(self.query_dict.urlencode(), '尾页'))

        return mark_safe(''.join(page_str_list))
