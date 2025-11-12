from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Ad, Material, Notification, InterviewPost, ReportedAd
from .serializers import (
    UserSerializer, AdSerializer, MaterialSerializer, NotificationSerializer,
    InterviewPostSerializer, ReportedAdSerializer
)
from .permissions import IsAdmin, IsFaculty, IsStudent, IsOwnerOrReadOnly

User = get_user_model()

def build_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    # Expect: username (or email), password, role, first_name/last_name optional
    data = request.data.copy()
    if not data.get('username'):
        data['username'] = data.get('email') or ''
    ser = UserSerializer(data=data)
    if ser.is_valid():
        user = ser.save()
        tokens = build_tokens(user)
        return Response({"user": UserSerializer(user).data, "tokens": tokens}, status=201)
    return Response({"errors": ser.errors}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')
    if not username or not password:
        return Response({"error":"Username/email and password required"}, status=400)
    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({"error":"Invalid credentials"}, status=401)
    tokens = build_tokens(user)
    return Response({"user": UserSerializer(user).data, "tokens": tokens})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)

class AdViewSet(viewsets.ModelViewSet):
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Ad.objects.select_related('owner').all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def mine(self, request):
        qs = Ad.objects.filter(owner=request.user).order_by('-created_at')
        return Response(self.get_serializer(qs, many=True).data)

class MaterialViewSet(viewsets.ModelViewSet):
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]
    queryset = Material.objects.select_related('uploader').all()

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)

class InterviewPostViewSet(viewsets.ModelViewSet):
    serializer_class = InterviewPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = InterviewPost.objects.select_related('author').all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class ReportedAdViewSet(viewsets.ModelViewSet):
    serializer_class = ReportedAdSerializer
    permission_classes = [IsAuthenticated]
    queryset = ReportedAd.objects.select_related('ad','reporter').all()

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdmin])
    def resolve(self, request, pk=None):
        r = self.get_object()
        r.resolved = True
        r.save()
        return Response({'status':'resolved'})
