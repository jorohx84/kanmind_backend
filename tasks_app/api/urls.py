from django.urls import path
from .views import TaskCreateView, TasksAssignedView, TasksReviewedView, CommentsView, CommentDeleteView
urlpatterns =[
    path('tasks/', TaskCreateView.as_view(), name="tasks"),
    path('tasks/assigned-to-me/', TasksAssignedView.as_view(), name="assigned-tasks"),
    path('tasks/reviewing/', TasksReviewedView.as_view(), name="reviewed-tasks"),
    path('tasks/<int:task_id>/comments/', CommentsView.as_view(), name="create-comments"),
    path('tasks/<int:task_id>/comments/<int:pk>/', CommentDeleteView.as_view(), name="delete-comments")
]