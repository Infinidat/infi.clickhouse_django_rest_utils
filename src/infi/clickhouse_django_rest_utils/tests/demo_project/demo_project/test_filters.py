from test_base import BaseTestCase
from infi.clickhouse_orm.database import Database
from django.conf import settings
from django.utils import timezone
from models import ClickhouseAllFields, enum_
import json


class FieldsTestCase(BaseTestCase):

    values_to_insert = [{
        'id': 1,
        'timestamp': timezone.now(),
        'timestamp_date': timezone.now().date(),
        'string_field': 'a',
        'intfield': 5,
        'floatfield': 0.5,
        'null_field': 'b',
        # populate enum_field with the first value in enum_
        'enum_field': list(enum_)[0]
    },{
        'id': 2,
        'timestamp': timezone.now(),
        'timestamp_date': timezone.now().date(),
        'string_field': 'c',
        'intfield': 10,
        'floatfield': 0.1,
        'null_field': 'd',
        # populate enum_field with the first value in enum_
        'enum_field': list(enum_)[0]
    },
    ]


    def setUp(self):
        super(FieldsTestCase, self).setUp()
        self.login()
        self.db = Database('test', settings.CLICKHOUSE_URL)
        self.db.create_table(ClickhouseAllFields)
        object1 = ClickhouseAllFields(**self.values_to_insert[0])
        object2 = ClickhouseAllFields(**self.values_to_insert[1])
        self.db.insert([object1, object2])



    def tearDown(self):
        self.db.drop_table(ClickhouseAllFields)
        self.db.drop_database()


    def test_effective_filter(self):
        res = self.client.get('/api/rest/allfields/', {'string_field': 'eq:a'})
        result = json.loads(res.content)['result']
        self.assertTrue(result)


    def test_not_effective_filter(self):
        res = self.client.get('/api/rest/allfields/', {'string_field': 'eq:z'})
        result = json.loads(res.content)['result']
        self.assertFalse(result)


    def test_filter_startswith(self):
        res = self.client.get('/api/rest/allfields/', {'null_field': 'starts with:b'})
        result = json.loads(res.content)['result']
        self.assertTrue(result)

    def test_filter_endsswith(self):
        res = self.client.get('/api/rest/allfields/', {'null_field': 'ends with:d'})
        result = json.loads(res.content)['result']
        self.assertTrue(result)


    def test_filterable_fields(self):
        # send a request with a filter which is not in the get_filterable_fields in the serializer of the view
        # to check that the request failed
        res = self.client.get('/api/rest/filterablefields/', {'id': 1})
        self.assertEqual(res.status_code, 400)
