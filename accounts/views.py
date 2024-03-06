from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Account, UserProfile
from .serializers import AccountSerializer, AccountSerializerWithToken, UserProfileSerializer
from .utils import send_confirmation_email


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_confirmed:
            raise AuthenticationFailed('Your account is not activated. Please confirm your account.')
        serializer = AccountSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v
        remember_me = self.context['request'].data.get('remember_me', False)
        if remember_me:
            token_lifetime = timedelta(days=settings.REMEMBER_ME_DAYS)
            refresh = RefreshToken.for_user(self.user)
            refresh.set_exp(lifetime=token_lifetime)
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
def registerUser(request):
    data = request.data
    required_fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']
    if not all(field in data for field in required_fields):
        return Response({'detail': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    if Account.objects.filter(email=data['email']).exists():
        return Response({'detail': 'Account with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Account.objects.create_user(
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data['phone_number'],
            email=data['email'],
            password=data['password']
        )
        user.generate_confirmation_token()
        send_confirmation_email(user.email, user.confirmation_token)
        # send_confirmation_email_task.delay(user.email, user.confirmation_token)

        serializer = AccountSerializerWithToken(user, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        message = {'detail': str(e)}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def confirm_email(request, token):
    """
    Confirm user email.
    """
    try:
        user = Account.objects.get(confirmation_token=token, is_confirmed=False)
        user.is_confirmed = True
        user.confirmation_token = ''  # Clear the token after successful confirmation
        user.save()

        return Response({'message': 'Email successfully confirmed'}, status=status.HTTP_200_OK)
    except Account.DoesNotExist:
        return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    """работает, пароль тоже"""
    user = request.user
    try:
        user_profile = user.userprofile
        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user, **request.data)
        serializer = UserProfileSerializer(user_profile)
    user.first_name = request.data.get('first_name', user.first_name)
    user.last_name = request.data.get('last_name', user.last_name)
    user.email = request.data.get('email', user.email)
    user.phone_number = request.data.get('phone_number', user.phone_number)
    user.save()

    if 'password' in request.data and request.data['password'] != '':
        user.password = make_password(request.data['password'])
    user.save()

    user_profile.refresh_from_db()
    could_sell = user_profile.is_complete()
    user_profile.could_sell = could_sell
    user_profile.save()

    response_data = {
        'account': AccountSerializerWithToken(user, many=False).data,
        'user_profile': serializer.data,
    }
    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    """Работает"""
    user = request.user
    user_profile = user.userprofile
    serializer = UserProfileSerializer(user_profile, many=False)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = Account.objects.all()
    serializer = AccountSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getUserById(request, email):
    print(request.data)
    try:
        user = Account.objects.get(email=email)
    except Account.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    password = request.data.get('password')
    if password is None:
        return Response({'error': 'Password not provided'}, status=400)

    if check_password(password, user.password):
        return Response({'verified': True})
    else:
        return Response({'verified': False}, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteUser(request):
    user = request.user
    try:
        user.delete()
        return Response({'message': 'Account deleted successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
