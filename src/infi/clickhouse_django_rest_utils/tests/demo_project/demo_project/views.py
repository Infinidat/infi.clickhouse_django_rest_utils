from __future__ import absolute_import
from builtins import object
from .models import ClickhouseAllFields
from infi.clickhouse_django_rest_utils.filters import ClickhouseFilterableField, ClickhouseRestFilter
from infi.clickhouse_django_rest_utils.serializers import ClickhouseSerializer
from infi.clickhouse_django_rest_utils.views import ClickhouseViewSet
from django.conf import settings
from infi.clickhouse_orm.database import Database

db = Database('test', settings.CLICKHOUSE_URL)

# CLASSES TO TEST SELECTION OF FIELDS USING THE __all__ VALUE

class AllFieldsSerializer(ClickhouseSerializer):
    class Meta:
        model = ClickhouseAllFields
        fields = '__all__'


class AllFieldsDataView(ClickhouseViewSet):
    queryset = ClickhouseAllFields.objects_in(db)
    serializer_class = AllFieldsSerializer

# CLASSES TO TEST SELECTION OF FIELDS USING THE FIELDS ARGUMENT

PARTIAL_FIELDS = ['string_field', 'intfield']


class PartOfFieldsSerializer(ClickhouseSerializer):
    class Meta:
        model = ClickhouseAllFields
        fields = PARTIAL_FIELDS


class PartialFieldsDataView(ClickhouseViewSet):
    queryset = ClickhouseAllFields.objects_in(db)
    serializer_class = PartOfFieldsSerializer

# CLASSES TO TEST SELECTION OF FIELDS USING THE EXCLUDE ARGUMENT

EXCLUDE_FIELDS = ['string_field', 'intfield']


class ExcludeFieldsSerializer(ClickhouseSerializer):
    class Meta:
        model = ClickhouseAllFields
        exclude = EXCLUDE_FIELDS


class ExcludeFieldsDataView(ClickhouseViewSet):
    queryset = ClickhouseAllFields.objects_in(db)
    serializer_class = ExcludeFieldsSerializer

# CLASSES TO TEST THE SPECIFIC FILTERS COMPATIBILITY

class SpecificFiltersSerializer(ClickhouseSerializer):
    class Meta:
        model = ClickhouseAllFields
        fields = '__all__'

    def get_filterable_fields(self):
        return [ClickhouseFilterableField('intfield', ClickhouseFilterableField.INTEGER)]



class SpecificFiltersDataView(ClickhouseViewSet):
    queryset = ClickhouseAllFields.objects_in(db)
    serializer_class = SpecificFiltersSerializer

