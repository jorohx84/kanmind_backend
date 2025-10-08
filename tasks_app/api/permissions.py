from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied
from boards_app.models import Board
from ..models import Task


class IsBoardMember(permissions.BasePermission):
    message = "You must be a member of the board to perform this action."

    def has_permission(self, request, view):
        board_id = request.data.get('board')
    

        if not board_id:
            task_id = view.kwargs.get('task_id') or view.kwargs.get('pk')
            if not task_id:
                return False

            try:
                task = Task.objects.get(pk=task_id)
                board = task.board
     
            except Task.DoesNotExist:
                raise NotFound("Task not found.")
        else:
            try:
                board = Board.objects.get(pk=board_id)
            except Board.DoesNotExist:
                raise NotFound("Board not found.")

        is_member = board.members.filter(pk=request.user.pk).exists()
        return is_member
    

class IsBoardOwnerOrMemberAndImmutableBoard(permissions.BasePermission):
    """
    Object-level permission to allow only Board owner or members to edit Tasks.

    Restrictions:
    - Only the board owner or members can have permission.
    - The task’s board association ('board' field) cannot be changed once set.

    Raises:
    - PermissionDenied if the user is not owner or member.
    - PermissionDenied if attempting to change the task's board.
    """

    message = "Only the Board owner or a member may edit this task. Changing the board association is not allowed."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (obj.board.owner == user or user in obj.board.members.all()):
            raise PermissionDenied(self.message)

        if request.method in ['PATCH', 'PUT']:
            new_board_id = request.data.get('board')
            if new_board_id and int(new_board_id) != obj.board.id:
                raise PermissionDenied("Changing the board association is not allowed.")

        return True

class IsCommentAuthor(permissions.BasePermission):
    """
    Object-level permission to allow only the author of a comment to perform actions.

    Returns True if the requesting user is the author of the comment, otherwise False.
    """

    message = "Only the author of the comment can perform this action."

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
