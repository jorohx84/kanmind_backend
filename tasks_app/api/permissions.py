from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied
from boards_app.models import Board
from ..models import Task


# class IsBoardMember(permissions.BasePermission):
#     """
#     Permission to check if the user is a member or owner of a Board.

#     Permission is granted if:
#     - For POST, PUT, PATCH requests: the board ID is extracted from request.data['board'].
#     - For GET, DELETE requests: the board ID is extracted from the view's URL kwargs (either 'pk' or 'board_id').

#     Then it checks if:
#     - The board exists.
#     - The user is either the board owner or a member of the board.

#     If the board does not exist, a NotFound exception is raised.
#     """

#     def has_permission(self, request, view):
#         board_id = None

#         if request.method in ['POST', 'PUT', 'PATCH']:
#             board_id = request.data.get('board')
#         elif request.method in ['GET', 'DELETE']:
#             board_id = view.kwargs.get('pk') or view.kwargs.get('board_id')

#         if not board_id:
#             return False

#         try:
#             board = Board.objects.get(pk=board_id)
#         except Board.DoesNotExist:
#             raise NotFound("Board not found.")

#         user = request.user
#         return user in board.members.all()
    

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
