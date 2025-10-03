from tasks_app.models import Task, Comment
from rest_framework import generics, permissions, status
from .serializers import TaskCreateUpdateSerializer, TaskDetailSerializer, CommentCreateSerielizer
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied
from .permissions import IsBoardMember, IsBoardOwnerOrMemberAndImmutableBoard, IsCommentAuthor

class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsBoardMember]


class TaskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMemberAndImmutableBoard]

    def get_object(self, pk):
        try:
            obj = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise NotFound("Task nicht gefunden.")

        user = self.request.user
        if not (obj.assignee == user or obj.board.owner == user):
            raise PermissionDenied("Keine Berechtigung, diese Task zu bearbeiten oder zu löschen.")
        return obj

    def get(self, request, pk, format=None):
        task = self.get_object(pk)
        serializer = TaskDetailSerializer(task)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        task = self.get_object(pk)
        serializer = TaskCreateUpdateSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        task = self.get_object(pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



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
    permission_classes = [permissions.IsAuthenticated, IsBoardMember]

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
    

class CommentDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthor]

    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return None

    def delete(self, request, task_id, pk):
        comment = self.get_object(pk)
        if not comment:
            return Response({"detail": "Kommentar nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, comment)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)