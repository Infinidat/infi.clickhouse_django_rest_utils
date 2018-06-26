from __future__ import absolute_import
from .test_base import BaseTestCase

from django.conf import settings
from infi.clickhouse_orm.database import Database
from .models import ClickhouseAllFields, enum_
from django.utils import timezone
from .views import AllFieldsSerializer
from dateutil import parser
from django.utils import six

class FieldsTestCase(BaseTestCase):
    # a script to test the serializer of clickhouse_django_rest_utils

    values_to_insert = {
        'id': 1,
        'timestamp': timezone.now(),
        'timestamp_date': timezone.now().date(),
        'string_field': 'aaaaa',
        'intfield': 5,
        'floatfield': 0.5,
        'null_field': 'bbbbb',
        # populate enum_field with the first value in enum_
        'enum_field': list(enum_)[0]
    }


    def setUp(self):
        self.db = Database('test', settings.CLICKHOUSE_URL)
        self.db.create_table(ClickhouseAllFields)
        self.object = ClickhouseAllFields(**self.values_to_insert)
        self.db.insert([self.object])


    def tearDown(self):
        self.db.drop_table(ClickhouseAllFields)
        self.db.drop_database()



    def test_simple_fields(self):
        simple_fields = ['string_field', 'intfield', 'floatfield']
        obj = ClickhouseAllFields.objects_in(self.db)[0]
        serialized = AllFieldsSerializer(obj)
        serialized_data = serialized.data
        for field in simple_fields:
            self.assertEqual(self.values_to_insert.get(field), serialized_data.get(field))


    def test_dates_fields(self):
        obj = ClickhouseAllFields.objects_in(self.db)[0]
        serialized = AllFieldsSerializer(obj)
        serialized_data = serialized.data
        for field in ['timestamp', 'timestamp_date']:
            self.assertEqual(parser.parse(serialized_data.get(field)).strftime("%Y-%m-%d %H:%M:%S"),
                             self.values_to_insert.get(field).strftime("%Y-%m-%d %H:%M:%S"))


    def test_nullable_field(self):
        obj = ClickhouseAllFields.objects_in(self.db)[0]
        serialized = AllFieldsSerializer(obj)

        self.assertEqual(serialized.data.get('null_field'), self.values_to_insert.get('null_field'))


    def test_enum_fields(self):
        obj = ClickhouseAllFields.objects_in(self.db)[0]
        serialized = AllFieldsSerializer(obj)
        self.assertEqual(serialized.data.get('enum_field'),
                         # take the name of the selected option in self.values_to_insert
                         self.values_to_insert.get('enum_field').name)
