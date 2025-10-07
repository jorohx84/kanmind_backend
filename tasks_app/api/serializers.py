from django.contrib.auth.models import User
from rest_framework import serializers
from tasks_app.models import Task, Comment
from user_auth_app.api.serializers import UserSerializer


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee', queryset=User.objects.all(), allow_null=True, required=False
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer', queryset=User.objects.all(), allow_null=True, required=False
    )

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
        ]



class TaskDetailSerializer(serializers.ModelSerializer):
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
        return obj.comments.count()


class CommentCreateSerielizer(serializers.ModelSerializer):
    author =serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "content", "created_at", "author"]

    def get_author(self, obj):
        return obj.author.get_full_name()