from rest_framework import serializers
from .models import User,Student_Registration,Post,Slider,EducationQualification

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model=Post
        fields='__all__'


class sliderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Slider
        fields='__all__'




class Student_info(serializers.ModelSerializer):
    class Meta:
        model=Student_Registration
        fields='__all__'


class Education_info(serializers.ModelSerializer):
    class Meta:
        model=EducationQualification
        fields='__all__'
