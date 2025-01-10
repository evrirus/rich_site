from .models import Jobs
from rest_framework import serializers

class JobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = '__all__'
