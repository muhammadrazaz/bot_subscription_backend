from rest_framework import serializers


class ProjectSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only = True)
    project_name = serializers.CharField(max_length = 50)
    total_cost = serializers.IntegerField(read_only = True)
    total_tasks = serializers.IntegerField(read_only = True)
    total_developers = serializers.IntegerField(read_only = True)