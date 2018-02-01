from test_base import BaseTestCase
from infi.clickhouse_orm.database import Database
from django.conf import settings
from django.utils import timezone
from models import ClickhouseAllFields, enum_
import json
from views import PARTIAL_FIELDS, EXCLUDE_FIELDS

class FieldsTestCase(BaseTestCase):

    values_to_insert = {
        'id': 1,
        'timestamp': timezone.now(),
        'timestamp_date': timezone.now().date(),
        'string_field': 'a',
        'intfield': 5,
        'floatfield': 0.5,
        'null_field': 'b',
        # populate enum_field with the first value in enum_
        'enum_field': list(enum_)[0]
    }

    def setUp(self):
        super(FieldsTestCase, self).setUp()
        self.login()
        self.db = Database('test', settings.CLICKHOUSE_URL)
        self.db.create_table(ClickhouseAllFields)
        object1 = ClickhouseAllFields(**self.values_to_insert)
        self.db.insert([object1])


    def tearDown(self):
        self.db.drop_table(ClickhouseAllFields)
        self.db.drop_database()


    def test_all_fields_exists(self):
        res = self.client.get('/api/rest/allfields/')
        result = json.loads(res.content)['result']
        # check that each key exists and stores a value
        for key, val in self.values_to_insert.items():
            # not comparing the values due to differences in case of datetime fields etc. that test is being done in
            # test_fields anyway
            self.assertIsNotNone(result[0].get(key))


    def test_partial_fields(self):
        res = self.client.get('/api/rest/partialfields/')
        result = json.loads(res.content)['result']
        for key in result[0].keys():
            self.assertTrue(key in PARTIAL_FIELDS)

    def test_exclude_fields(self):
        res = self.client.get('/api/rest/excludefields/')
        result = json.loads(res.content)['result']
        for key in EXCLUDE_FIELDS:
            self.assertFalse(key in result[0])