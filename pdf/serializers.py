from rest_framework import serializers
from .models import PDFFiles

class PDFSerializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p')
    class Meta:
        model = PDFFiles
        fields = '__all__'
class PDFUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True
    )

    def validate_files(self, files):
       
        for file in files:
            if file.content_type != 'application/pdf':
                raise serializers.ValidationError("All files must be in PDF format.")
        return files
    
class PDFUserDetailSerializer(serializers.Serializer):
     id = serializers.IntegerField()
     web_username = serializers.CharField()
     web_password = serializers.CharField()
     total_pdf = serializers.CharField()
     
    
