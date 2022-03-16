from rest_framework.serializers import ModelSerializer
from rest_framework.relations import HyperlinkedIdentityField
from wi.models import domain, area, task

class task_serializer(ModelSerializer):
    #area_url = HyperlinkedIdentityField(
    ##                view_name='wi:area_view',
    #                lookup_field='area',
    #)
    # NEXT: area looks like its some string, may have to parse that string or idk what

    class Meta:
        model = task
        #
        # display ordering purposes only
        #
        fields = ['id', 'priority', 'status', 'description', 'area', 'created_by', 'created', 'updated', 'completed']
        #fields = '__all__'



class area_serializer(ModelSerializer):

    class Meta:
        model = area
        fields = ['id', 'name', 'domain', ]

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