Overview
========
This project contains classes and utils making the django rest framwork compatible to work against a Clickhouse ORM.


Usage
-----
a. Add infi.clickhouse_django_rest_utils to the `INSTALLED_APPS` in your settings file:

```python
    INSTALLED_APPS = (
        ...
        'infi.clickhouse_django_rest_utils',
    )
```
b. Run the following commands:
    
    easy_install -U infi.projector
    projector devenv build

Running Tests
-------------
In order to run test go the folder:

    src/infi/clickhouse_django_rest_utils/tests/demo_project
and use this command to run the tests:

    ./manage.py test
    

serializers
===========
###ClickhouseSerializer
Extends the Django-rest-framework Serializer, adding it the compatibility to recognize Clickhouse fields.
######Supported Clickhouse ORM fields are:
- Int8Field
- Int16Field
- Int32Field
- Int64Field
- StringField
- Float32Field
- Float64Field
- DateTimeField
- DateField
- NullableField
- Enum8Field
- Enum16Field

######Not supported Fields:
- ArrayField


Supports in the following fields selection:
- fields = '__all __'
- fields = [< list of fields to include>]
- exclude = [< list of fields to exclude>]

- Omitting fields and exclude form the Meta class will be resulted in selecting all available fields in the model.

####ClickhouseSerializer usage example:

```python
class ClickhouseSerializerExample(ClickhouseSerializer):
    class Meta:
        model = SomeClickhouseModel
        # fields can be '__all__' or a list of fields
        # can have exclude instead of fields to indicate which fields to exclude 
        fields = '__all__'
```

    
views
=====
###ClickhouseViewSet
Extends the GenericViewSet and overrides the methods 
filter_queryset and list. 

The view is using the ClickhousePaginator as the pagination_class, and the ClickhouseRestFilter as its filters_backend.

####ClickhouseViewSet usage example:

```python
class ClickhouseViewSetExample(ClickhouseViewSet):
    queryset = Some_Clickhouse_valid_queryset
    serializer_class = SomeClickhouseSerializerClass
```

When using the ClickhouseViewSet it is mandatory to define 
a queryset(a valid Clickhouse ORM queryset) and a serializer_class(a valid ClickhouseSerializer) arguments that will be used during 
the view process. 

Please note that the Clickhouse viewset supports only in list method, and cannot return data for a single object query (i.e some-url-address/<obj_id>).


Filters
=======
###ClickhouseRestFilter
Extends the infi.django_rest_utils' InfinidatFilter, making it compatible to filter the given Clickhouse ORM queryset.

###ClickhouseOrderingFilter
Extends the infi.django_rest_utils' OrderingFilter and is adding a support to have sorted results in the Clickhouse Django REST Utils.
Implements the filter_queryset method and executes sorting on the given Clickhouse Queryset.

###ClickhouseFilterableField
A class representing a Clickhouse Filterable Field to be 
used when configuring the list of fields to filter in the 
serializer (using the get_filterable_fields method).

The most important method build_q which returns the field's query according to the Clickhouse ORM rules.



######Supported Operators:

- equal (eq)
- not equal (ne)
- lower than (lt)
- greater than (gt)
- grater equal than (ge)
- like (case sensitive) (icontains)
- unlike (case sensitive) (icontains)
- in (in)
- out (not_in)
- like (contains)
- unlike (contains)
- starts with (startswith)
- ends with (endswith)

