from django.contrib.auth.models import User
from rest_framework import serializers
from tasks_app.models import Task, Comment
from user_auth_app.api.serializers import UserSerializer


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Task instances.

    Fields:
    - id: Task ID (read-only)
    - board: ForeignKey to Board
    - title: Title of the task
    - description: Detailed description of the task
    - status: Current status of the task
    - priority: Priority level of the task
    - assignee_id: User assigned to the task (nullable, optional)
    - reviewer_id: User reviewing the task (nullable, optional)
    - due_date: Deadline for the task
    """
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee', queryset=User.objects.all(), allow_null=True, required=False
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer', queryset=User.objects.all(), allow_null=True, required=False
    )
    comments_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "due_date",
            "comments_count",
        ]


class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Task view including related user info and comments count.

    Fields:
    - id: Task ID
    - board: Related Board
    - title: Title of the task
    - description: Detailed description
    - status: Current status
    - priority: Priority level
    - assignee: Nested user serializer for the assigned user (read-only)
    - reviewer: Nested user serializer for the reviewer (read-only)
    - due_date: Deadline
    - comments_count: Number of comments related to this task (read-only)
    """
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        """Return the total number of comments related to this task."""
        return obj.comments.count()

class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for upadted Task view including related user info and comments count.

    Fields:
    - id: Task ID
    - title: Title of the task
    - description: Detailed description
    - status: Current status
    - priority: Priority level
    - assignee: Nested user serializer for the assigned user (read-only)
    - reviewer: Nested user serializer for the reviewer (read-only)
    - due_date: Deadline
    - comments_count: Number of comments related to this task (read-only)
    """
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
        ]

    


class CommentCreateSerielizer(serializers.ModelSerializer):
    """
    Serializer for creating and reading Comment instances.

    Fields:
    - id: Comment ID
    - content: Text content of the comment
    - created_at: Timestamp when the comment was created
    - author: Full name of the comment author (read-only)
    """
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "content", "created_at", "author"]

    def get_author(self, obj):
        """Return the full name of the comment author."""
        return obj.author.get_full_name()
