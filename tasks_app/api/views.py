from tasks_app.models import Task, Comment
from rest_framework import generics, permissions, status
from .serializers import TaskCreateUpdateSerializer, TaskDetailSerializer, CommentCreateSerielizer
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied



class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]


class TasksAssignedView(generics.ListAPIView):
    serializer_class = TaskDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assignee=user)

class TasksReviewedView(generics.ListAPIView):
    serializer_class = TaskDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer=user)
    
class CommentsView(generics.ListCreateAPIView):
    serializer_class = CommentCreateSerielizer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get("task_id")
        return Comment.objects.filter(task_id=task_id)
    
    def create(self, request, *args, **kwargs):
        task_id = kwargs.get("task_id")
        task = generics.get_object_or_404(Task, id=task_id)

        if request.user not in task.board.members.all():
            return Response({"detail": "Du bist kein Mitglied dieses Boards."},
                        status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, task=task)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        pk = self.kwargs.get("pk")
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Kommentar nicht gefunden.")

        user = self.request.user
        if comment.author != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Du hast keine Berechtigung, diesen Kommentar zu löschen.")

        return comment  

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)