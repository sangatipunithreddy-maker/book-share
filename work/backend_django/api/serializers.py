from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Ad, Material, Notification, InterviewPost, ReportedAd

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=4)
    class Meta:
        model = User
        fields = ('id','username','email','password','first_name','last_name','role','year','branch')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class AdSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Ad
        fields = ('id','owner','title','description','price','created_at')

class MaterialSerializer(serializers.ModelSerializer):
    uploader = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Material
        fields = ('id','uploader','name','url','created_at')

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id','message','read','created_at')

class InterviewPostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = InterviewPost
        fields = ('id','author','title','body','created_at')

class ReportedAdSerializer(serializers.ModelSerializer):
    reporter = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = ReportedAd
        fields = ('id','ad','reporter','reason','resolved','created_at','updated_at')
