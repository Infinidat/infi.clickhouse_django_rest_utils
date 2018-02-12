from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.utils.urls import remove_query_param, replace_query_param
from collections import OrderedDict
from rest_framework.response import Response
from infi.django_rest_utils import pagination
from django.utils import six
from filters import ClickhouseRestFilter, clickhouseOrderingFilter
from django.core.paginator import InvalidPage
from rest_framework.viewsets import ReadOnlyModelViewSet
from infi.django_rest_utils.views import ViewDescriptionMixin


class ClickhousePaginator(pagination.InfinidatPaginationSerializer):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('number_of_objects', self.number_of_objects),
            ('page_size', self.page_size),
            ('pages_total', self.pages_total),
            ('page', self.page_number),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


    def get_next_link(self):
        if not self.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = int(self.page_number) + 1
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = int(self.page_number) - 1
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)


    def has_next(self):
        return int(self.page_number) < self.pages_total

    def has_previous(self):
        return int(self.page_number) > 1


    def paginate_queryset(self, queryset, request, view=None):
        self.request = request

        page_size = self.get_page_size(request)
        if not page_size:
            return None

        page_number = request.query_params.get(self.page_query_param, 1)


        self.page = queryset.paginate(page_num=int(page_number),
                                      page_size=int(page_size))

        if self.page.pages_total and int(page_number) > int(self.page.pages_total):
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(InvalidPage)
            )
            raise NotFound(msg)

        self.number_of_objects = self.page.number_of_objects
        self.page_size = self.page.page_size
        self.pages_total = self.page.pages_total
        self.page_number = self.page.number

        return self.page.objects

class ClickhouseViewSet(ViewDescriptionMixin, ReadOnlyModelViewSet):
    pagination_class = ClickhousePaginator
    # to be used in the ViewDescriptionMixin
    filter_backends = [ClickhouseRestFilter, clickhouseOrderingFilter]


    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, *args, **kwargs):
        self.request = request
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        self.page = self.paginate_queryset(queryset)
        if self.page is not None:
            serializer = self.get_serializer(self.page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)