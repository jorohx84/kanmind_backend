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

        Args:
            request: The HTTP request being processed.
            view: The view handling the request.
            obj: The board object for which permission is being checked.

        Returns:
            bool: True if the user is the owner or a member of the board,
                  False otherwise.
        """
        return (
            obj.owner == request.user or
            request.user in obj.members.all()
        )