from django.urls import path
from .views import SignupView, UserLoginView, MailCheckView

urlpatterns = [
path('registration/', SignupView.as_view(), name="signup"),
path('login/', UserLoginView.as_view(), name='login'),
path('email-check/', MailCheckView.as_view(), name='email-check'),
]