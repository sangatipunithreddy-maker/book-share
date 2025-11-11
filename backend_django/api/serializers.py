from rest_framework import serializers
from .models import User, Ad, Material, Notification, InterviewPost, ReportedAd

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id','name','email','role','year','branch')
    def get_name(self, obj):
        return obj.get_full_name() or obj.username

class AdSerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)
    seller_id = serializers.PrimaryKeyRelatedField(source='seller', queryset=User.objects.all(), write_only=True, required=False)
    class Meta:
        model = Ad
        fields = ('id','title','description','price','status','seller','seller_id','created_at','updated_at')

class MaterialSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    uploaded_by_id = serializers.PrimaryKeyRelatedField(source='uploaded_by', queryset=User.objects.all(), write_only=True, required=False)
    class Meta:
        model = Material
        fields = ('id','subject','semester','academic_year','filename','verified','uploaded_by','uploaded_by_id','created_at','updated_at')

class InterviewPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(source='author', queryset=User.objects.all(), write_only=True, required=False)
    class Meta:
        model = InterviewPost
        fields = ('id','title','content','author','author_id','created_at','updated_at')

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id','user','content','read','created_at','updated_at')

class ReportedAdSerializer(serializers.ModelSerializer):
    ad = AdSerializer(read_only=True)
    reporter = UserSerializer(read_only=True)
    ad_id = serializers.PrimaryKeyRelatedField(source='ad', queryset=Ad.objects.all(), write_only=True)
    class Meta:
        model = ReportedAd
        fields = ('id','ad','ad_id','reporter','reason','resolved','created_at','updated_at')
