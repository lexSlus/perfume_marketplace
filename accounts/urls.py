from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', views.registerUser, name='register'),
    path('profile/', views.getUserProfile, name="user-profile"),
    path('profile/update/', views.updateUserProfile, name="user-profile-update"),
    path('', views.getUsers, name="users"),
    path('delete/', views.deleteUser, name='user-delete'),
    path('<str:email>/', views.getUserById, name='user-detail'),

    # path('reset-password/', requestResetPassword, name='request_reset_password'),
    # path('reset-password-confirm/<str:token>/', confirm_password_reset, name='confirm-email'),

]
