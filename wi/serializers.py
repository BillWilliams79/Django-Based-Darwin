from rest_framework.serializers import ModelSerializer
from rest_framework.relations import HyperlinkedIdentityField
from wi.models import domain, area, task

class area_class_serializer(ModelSerializer):
    
    class Meta:
        model = area
        fields = '__all__'

class domain_class_serializer(ModelSerializer):
    
    class Meta:
        model = domain
        fields = '__all__'

class task_class_serializer(ModelSerializer):
    
    class Meta:
        model = task
        fields = '__all__'        