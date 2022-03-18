from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField
from wi.models import domain, area, task
from django.contrib.auth.models import User
from users.models import Profile

class domain_class_serializer(serializers.ModelSerializer):

    # worked to generate the pk? why would i need this
    #
    #created_by = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    
    created_by = serializers.StringRelatedField()

    class Meta:
        model = domain
        fields = '__all__'


class area_class_serializer(serializers.ModelSerializer):

    #
    # StringRelatedField(): retrieves the string name from the models.py.
    #      expect your models' __str__ result to be present in JSON
    # set many = True to iterate on the field, such as many to many foreign key
    created_by = serializers.StringRelatedField()

    domain = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='wi:rest_domain'
    )


    class Meta:
        model = area
        fields = '__all__'


class task_class_serializer(serializers.ModelSerializer):
    
    created_by = serializers.StringRelatedField()

    area = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='wi:rest_area'
    )
    class Meta:
        model = task
        fields = '__all__'


class user_class_serializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'

class profile_class_serializer(serializers.ModelSerializer):
    
    user = serializers.StringRelatedField()
    
    class Meta:
        model = Profile
        fields = '__all__'


