from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from boards_app.models import Board
from .permissions import IsBoardOwnerOrMember
from .serializers import BoardSerializer, SingleBoardSerializer, BoardUpdateSerializer

class BoardCreateView(generics.ListCreateAPIView):
    """
    API view to list all boards the authenticated user owns or is a member of,
    and to create new boards.

    Permissions:
    - Only authenticated users can access this view.

    Methods:
    - GET: Returns a list of boards filtered by ownership or membership.
    - POST: Creates a new board with the authenticated user as the owner.
    """
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Return boards where user is owner or a member
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        # Save the board with the current user as owner handled in serializer
        serializer.save()


class BoardDetailView(APIView):
    """
    API view to retrieve, update (partial), or delete a specific board.

    Permissions:
    - Only authenticated users who are the board owner or a member can access.
    
    Methods:
    - GET: Retrieve the detailed data of the board.
    - PATCH: Partially update the board data.
    - DELETE: Delete the board.
    """

    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]

    def get_object_and_check_permissions(self, pk):
        """
        Retrieve the Board object by primary key and check object-level permissions.
        Raises NotFound if board does not exist.
        """
        try:
            board = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            raise NotFound("Board not found.")
        self.check_object_permissions(self.request, board)
        return board

    def get(self, request, pk):
        board = self.get_object_and_check_permissions(pk)
        serializer = SingleBoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        board = self.get_object_and_check_permissions(pk)
        serializer = BoardUpdateSerializer(board, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        board = self.get_object_and_check_permissions(pk)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)