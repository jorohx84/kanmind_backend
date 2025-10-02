from rest_framework import serializers
from boards_app.models import Board
from django.contrib.auth.models import User
from user_auth_app.api.serializers import UserSerializer
from tasks_app.api.serializers import TaskDetailSerializer


class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), write_only=True) 

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
        read_only_fields = ["id", "member_count", "ticket_count", "tasks_to_do_count", "tasks_high_prio_count", "owner"]
    
    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        # später durch tatsächliche Tickets ersetzen
        return 0

    def get_tasks_to_do_count(self, obj):
        # später durch echte Tasks ersetzen
        return 0

    def get_tasks_high_prio_count(self, obj):
        # später durch echte Tasks ersetzen
        return 0
    
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        members = validated_data.pop("members",[])
        board = Board.objects.create(owner=user, **validated_data)
        for member in members:
            board.members.add(member)
        return board
    

class SingleBoardSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskDetailSerializer (many=True, read_only=True)

    class Meta:
        model = Board
        fields = fields = ["id", "title", "owner_id", "members", "tasks"]