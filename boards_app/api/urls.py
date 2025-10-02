from django.urls import path
from .views import BoardCreateView, BoardDetailView



urlpatterns = [
    path('boards/', BoardCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
]





