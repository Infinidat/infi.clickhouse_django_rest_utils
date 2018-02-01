from infi.clickhouse_orm import fields as chf
from infi.django_rest_utils import filters
from rest_framework.exceptions import NotFound, ValidationError





class ClickhouseFilterableField(object):

    STRING   = 'string'
    INTEGER  = 'integer'
    FLOAT    = 'float'
    BOOLEAN  = 'boolean'
    DATETIME = 'datetime'

    def __init__(self, name, source=None, converter=None, datatype=STRING, advanced=False):
        self.name = name
        self.source = source or name
        self.converter = converter or (lambda value: value)
        self.datatype = datatype
        self.advanced = advanced


    def build_q(self, orm_operator, value):
        value = self.convert(value)
        return {'{}__{}'.format(self.source, orm_operator): value}

    def convert(self, value):
        if isinstance(value, list):
            return [self.converter(v) for v in value]
        else:
            return self.converter(value)



class ClickhouseRestFilter(filters.InfinidatFilter):

    def filter_queryset(self, request, queryset, view):
        # get a list of all fields to filter
        filterable_fields = _get_filterable_fields(view)
        ignored_fields = self._get_ignored_fields(view)
        for field_name in request.GET.keys():
            if field_name in ignored_fields:
                continue
            field = None
            for f in filterable_fields:
                if field_name == f.name:
                    field = f
                    break
            if not field:
                # raise exception if didn't find the given field in the filterable fields
                names = [f.name for f in filterable_fields]
                raise ValidationError("Unknown filter field: '%s' (choices are %s)" % (field_name, ', '.join(names)))
            for expr in request.GET.getlist(field_name):
                queryset = self._apply_filter(queryset, field, expr)
        return queryset


    def _apply_filter(self, queryset, field, expr):
        q, negate = self._build_q(field, expr)
        try:
            return queryset.exclude(**q).distinct() if negate else queryset.filter(**q).distinct()
        except (ValueError):
            raise ValidationError(field.name + ': the given operator or value are inappropriate for this field')


    def _get_operators(self):
        return [
            filters.Operator('eq',      'eq',       'field = value'),
            filters.Operator('ne',      'ne',       'field <> value'),
            filters.Operator('lt',      'lt',        'field < value'),
            filters.Operator('le',      'lte',       'field <= value'),
            filters.Operator('gt',      'gt',        'field > value'),
            filters.Operator('ge',      'gte',       'field >= value'),
            filters.Operator('like(case sensitive)',    'icontains', 'field contains a string (case insensitive)'),
            filters.Operator('unlike(case sensitive)',  'icontains', 'field does not contain a string (case insensitive)', negate=True),
            filters.Operator('in',      'in',        'field is equal to one of the given values', max_vals=1000),
            filters.Operator('out',     'not_in',     'field is not equal to any of the given values', max_vals=1000),
            filters.Operator('like', 'contains', 'field contains a string'),
            filters.Operator('unlike', 'contains', 'field does not contain a string', negate=True),
            filters.Operator('starts with', 'startswith', 'field is starting with the given value'),
            filters.Operator('ends with', 'endswith', 'field is ending with the given value')
        ]

def _get_filterable_fields(view):
    '''
    Get the list of filterable fields for the given view, or deduce them
    from the serializer fields.
    '''
    serializer = view.get_serializer()
    if hasattr(serializer, 'get_filterable_fields'):
        return serializer.get_filterable_fields()
    # Autodetect filterable fields according to all available fields in the serializers
    return [
        ClickhouseFilterableField(field.source or field_name, datatype=_get_field_type(field))
        for field_name, field in serializer.fields.items()
        if not getattr(field, 'write_only', False) and not field.source == '*'
    ]


def _get_field_type(serializer_field):
    '''
    Determine the appropriate FilterableField type for the given serializer field.
    '''
    if isinstance(serializer_field, chf.BaseIntField):
        return ClickhouseFilterableField.INTEGER
    if isinstance(serializer_field, chf.BaseFloatField):
        return ClickhouseFilterableField.FLOAT
    if isinstance(serializer_field, chf.DateTimeField):
        return ClickhouseFilterableField.DATETIME
    return ClickhouseFilterableField.STRING