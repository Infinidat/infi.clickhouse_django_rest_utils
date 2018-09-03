from rest_framework import serializers
from infi.clickhouse_orm import fields as chf
from collections import OrderedDict


class ClickhouseSerializer(serializers.Serializer):
    serializer_field_mapping = {
        chf.Int8Field: serializers.IntegerField,
        chf.Int16Field: serializers.IntegerField,
        chf.Int32Field: serializers.IntegerField,
        chf.Int64Field: serializers.IntegerField,
        chf.StringField: serializers.CharField,
        chf.Float32Field: serializers.FloatField,
        chf.Float64Field: serializers.FloatField,
        chf.DateTimeField: serializers.DateTimeField,
        chf.DateField: serializers.DateField,
        chf.UInt8Field: serializers.IntegerField,
        chf.UInt16Field: serializers.IntegerField,
        chf.UInt32Field: serializers.IntegerField,
        chf.UInt64Field: serializers.IntegerField
    }

    def clickhouse_field_to_django(self, field_type):
        '''convert the given clickhouse field to a serializer field'''

        # support in nullable fields: find the type of the inner field
        if field_type.__class__ == chf.NullableField:
            field_type = field_type.inner_field
        # support in Array fields: checks its inner field and convert to a ListField
        if field_type.__class__ == chf.ArrayField:
            field_inside_array = self.clickhouse_field_to_django(field_type.inner_field)
            return serializers.ListField(child=field_inside_array)

        # find a matching according to self.serializer_field_mapping: if not found checks for 'django_field_type' in the given field class or returns a default CharField
        return self.serializer_field_mapping.get(field_type.__class__,
                                                 # take django_field_type attr from the field cls
                                                 field_type.__class__.django_field_type
                                                 # if missing, default type is Char
                                                 if hasattr(field_type.__class__, 'django_field_type')
                                                 else serializers.CharField)()

    def get_fields(self):
        fields_res = OrderedDict()
        model = getattr(self.Meta, 'model')
        fields = getattr(self.Meta, 'fields', [])
        exclude = getattr(self.Meta, 'exclude', [])

        for f in model._fields.items():
            field_name = f[0]
            field_type = f[1]
            # check for each field in the model if it should be included in the fields results or not according to Meta.fields and Meta.exclude
            if fields == serializers.ALL_FIELDS or ((fields and field_name in fields) or not fields):
                if (exclude and field_name not in exclude) or not exclude:
                    if issubclass(field_type.__class__, chf.BaseEnumField):
                        # runs over all values of the enum and create a valid serializers.ChoiceField
                        enum_values = list(field_type.enum_cls)
                        list_of_choices = [val.name for val in enum_values]
                        fields_res[field_name] = ChoiceFieldToString(choices=list_of_choices)

                    else:
                        fields_res[field_name] = self.clickhouse_field_to_django(field_type)
        return fields_res


class ChoiceFieldToString(serializers.ChoiceField):
    def to_representation(self, value):
        '''
        overrides this function in order to return the string value of the selected option of the choice field
        :param value: the given option
        :return: the name of the option
        '''
        if value in ('', None):
            return value
        return value.name

