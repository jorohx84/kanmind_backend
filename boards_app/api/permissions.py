from rest_framework import permissions


class IsBoardOwnerOrMember(permissions.BasePermission):
    """
    Custom permission to allow access only to the owner of the board
    or members of the board.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the requesting user is either the owner of the board
        or a member of the board.
        """
        return (
            obj.owner == request.user or
            request.user in obj.members.all()
        )