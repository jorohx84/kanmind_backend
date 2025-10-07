from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied
from boards_app.models import Board


class IsBoardMember(permissions.BasePermission):

    def has_permission(self, request, view):
        board_id = None

        if request.method in ['POST', 'PUT', 'PATCH']:
            board_id = request.data.get('board')
        elif request.method in ['GET', 'DELETE']:
            board_id = view.kwargs.get('pk') or view.kwargs.get('board_id')

        if not board_id:
            return False

        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            raise NotFound("Board nicht gefunden.")

        user = request.user
        return board.owner == user or user in board.members.all()
    

class IsBoardOwnerOrMemberAndImmutableBoard(permissions.BasePermission):

    message = "Nur der Board-Eigentümer oder ein Board-Mitglied dürfen diese Task bearbeiten. Die Board-Zuordnung darf nicht geändert werden."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (obj.board.owner == user or user in obj.board.members.all()):
            raise PermissionDenied(self.message)

        if request.method in ['PATCH', 'PUT']:
            new_board_id = request.data.get('board')
            if new_board_id and int(new_board_id) != obj.board.id:
                raise PermissionDenied("Ändern der Board-Zuordnung ist nicht erlaubt.")

        return True

class IsCommentAuthor(permissions.BasePermission):
    message = "Nur der Autor des Kommentars darf diese Aktion durchführen."

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user