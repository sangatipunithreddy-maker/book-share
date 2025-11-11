from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
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

def token_for(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    name  = request.data.get('name')
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role', 'student')
    year = request.data.get('year')
    branch = request.data.get('branch')
    if not name or not email or not password or not role:
        return Response({'error':'Missing fields'}, status=400)
    parts = (name or '').strip().split(' ', 1)
    first_name = parts[0] if parts else ''
    last_name = parts[1] if len(parts)>1 else ''
    try:
        user = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password),
            role=role,
            year=year or None,
            branch=branch or None,
        )
    except Exception as e:
        if 'UNIQUE' in str(e).upper():
            return Response({'error':'Email already exists'}, status=409)
        return Response({'error':'Server error'}, status=500)
    token = token_for(user)
    return Response({'token': token, 'user': UserSerializer(user).data}, status=201)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error':'Invalid email or password'}, status=401)
    if role and user.role != role:
        return Response({'error':'Role mismatch'}, status=401)
    if not check_password(password, user.password):
        return Response({'error':'Invalid email or password'}, status=401)
    token = token_for(user)
    return Response({'token': token, 'user': UserSerializer(user).data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = User.objects.get(id=request.user.id)
    return Response({'user': UserSerializer(user).data})

# ====== ViewSets ======
class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.select_related('seller').order_by('-created_at')
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated & IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    @action(detail=False, methods=['get'])
    def mine(self, request):
        qs = self.queryset.filter(seller=request.user)
        return Response(self.get_serializer(qs, many=True).data)

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.select_related('uploaded_by').order_by('-created_at')
    serializer_class = MaterialSerializer

    def get_permissions(self):
        if self.request.method in ('POST','PUT','PATCH','DELETE'):
            # only faculty can create; admin can verify/update; owners can edit their own
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        # faculty uploads
        serializer.save(uploaded_by=self.request.user, verified=False)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdmin])
    def verify(self, request, pk=None):
        m = self.get_object()
        m.verified = True
        m.save()
        return Response({'status':'verified'})

class InterviewPostViewSet(viewsets.ModelViewSet):
    queryset = InterviewPost.objects.select_related('author').order_by('-created_at')
    serializer_class = InterviewPostSerializer
    permission_classes = [IsAuthenticated & IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet, mixins.UpdateModelMixin):
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        n = self.get_object()
        n.read = True
        n.save()
        return Response({'status':'ok'})

class ReportedAdViewSet(viewsets.ModelViewSet):
    queryset = ReportedAd.objects.select_related('ad','reporter').order_by('-created_at')
    serializer_class = ReportedAdSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdmin])
    def resolve(self, request, pk=None):
        r = self.get_object()
        r.resolved = True
        r.save()
        return Response({'status':'resolved'})
