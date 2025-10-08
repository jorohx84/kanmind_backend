from django.contrib.auth.models import User
from rest_framework import serializers
from boards_app.models import Board
from tasks_app.api.serializers import TaskDetailSerializer
from user_auth_app.api.serializers import UserSerializer


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for Board model.
    Used for creating and updating boards, includes member management
    and several computed count fields.
    """
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]
        read_only_fields = [
            "id",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner"
        ]

    def get_member_count(self, obj):
        """Return the number of members in the board."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the number of tickets in the board (currently returns 0)."""
        return 0

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks to do in the board (currently returns 0)."""
        return 0

    def get_tasks_high_prio_count(self, obj):
        """Return the number of high priority tasks in the board (currently returns 0)."""
        return 0
    
    def create(self, validated_data):
        """
        Create a new board instance, setting the owner as the request user,
        and adding any members specified in the request.
        """
        request = self.context.get("request")
        user = request.user
        members = validated_data.pop("members", [])
        board = Board.objects.create(owner=user, **validated_data)
        for member in members:
            board.members.add(member)
        return board
    

class SingleBoardSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed board view.
    Includes nested serializers for members and tasks (read-only).
    """
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskDetailSerializer(many=True, read_only=True)
    

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]



class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer used for updating a Board instance via PATCH requests.

    - Accepts a list of member user IDs in the 'members' field (write-only).
    - Returns detailed user data for the updated members via 'members_data'.
    - Returns detailed user data for the board owner via 'owner_data'.
    - This serializer is intended only for updating board title and members.
    """
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True
    )
    members_data = UserSerializer(source='members', many=True, read_only=True)
    owner_data = UserSerializer(source='owner', read_only=True)

    class Meta:
        model = Board
        fields = [
            "id", "title",
            "members",       
            "members_data",  
            "owner_data",    
        ]