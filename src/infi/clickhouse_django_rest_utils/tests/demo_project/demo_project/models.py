from infi.clickhouse_orm import models as chm
from infi.clickhouse_orm import fields as chf
from infi.clickhouse_orm.engines import MergeTree
import enum



enum_ = enum.Enum('enum_options', ['one', 'two', 'three'])

#todo: add all kinds of clickhouse fields
class ClickhouseAllFields(chm.Model):

    id = chf.Int64Field()
    timestamp = chf.DateTimeField()
    timestamp_date = chf.DateField()
    string_field = chf.StringField()
    intfield = chf.Int32Field()
    floatfield = chf.Float32Field()
    null_field = chf.NullableField(chf.StringField())
    enum_field = chf.Enum16Field(enum_)


    engine = MergeTree('timestamp_date', ['id'])