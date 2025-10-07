from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from tasks_app.models import Task, Comment
from .permissions import IsBoardMember, IsBoardOwnerOrMemberAndImmutableBoard, IsCommentAuthor
from .serializers import TaskCreateUpdateSerializer, TaskDetailSerializer, CommentCreateSerielizer


class TaskCreateView(generics.CreateAPIView):
    """
    API endpoint to create a new Task.

    Permissions:
    - User must be authenticated.
    - User must be a member of the associated Board.
    """
    queryset = Task.objects.all()
    serializer_class = TaskCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsBoardMember]


class TaskDetailView(APIView):
    """
    API endpoint to retrieve, update (partial), or delete a Task by its ID.

    Permissions:
    - User must be authenticated.
    - User must be Board owner or member.
    - Board assignment cannot be changed on update.
    """
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMemberAndImmutableBoard]

    def get_object(self, pk):
        """Retrieve Task by primary key or raise NotFound if it does not exist."""
        try:
            obj = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")
        return obj

    def get(self, request, pk, format=None):
        """Return task details."""
        task = self.get_object(pk)
        serializer = TaskDetailSerializer(task)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        """Partially update a task."""
        task = self.get_object(pk)
        serializer = TaskCreateUpdateSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """Delete a task."""
        task = self.get_object(pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TasksAssignedView(generics.ListAPIView):
    """
    API endpoint to list all tasks assigned to the authenticated user.
    """
    serializer_class = TaskDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assignee=user)


class TasksReviewedView(generics.ListAPIView):
    """
    API endpoint to list all tasks the authenticated user is reviewing.
    """
    serializer_class = TaskDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer=user)


class CommentsView(generics.ListCreateAPIView):
    """
    API endpoint to list comments for a task and to create new comments.

    Permissions:
    - User must be authenticated.
    - User must be Board owner or member.
    """
    serializer_class = CommentCreateSerielizer
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMemberAndImmutableBoard]

    def get_queryset(self):
        task_id = self.kwargs.get("task_id")
        return Comment.objects.filter(task_id=task_id)

    def create(self, request, *args, **kwargs):
        task_id = kwargs.get("task_id")
        task = generics.get_object_or_404(Task, id=task_id)

        if request.user not in task.board.members.all():
            return Response({"detail": "You are not a member of this board."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, task=task)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDeleteView(APIView):
    """
    API endpoint to delete a comment by its ID.

    Permissions:
    - User must be authenticated.
    - User must be the author of the comment.
    """
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthor]

    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return None

    def delete(self, request, task_id, pk):
        comment = self.get_object(pk)
        if not comment:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, comment)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
