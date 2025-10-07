from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from boards_app.models import Board
from .permissions import IsBoardOwnerOrMember
from .serializers import BoardSerializer, SingleBoardSerializer

class BoardCreateView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        serializer.save()

    

class BoardDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]

    def get_object_and_check_permissions(self, pk):
        try:
            board = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            raise NotFound("Board nicht gefunden.")
    
        self.check_object_permissions(self.request, board)
        return board

    def get(self, request, pk):
        board = self.get_object_and_check_permissions(pk)
        serializer = SingleBoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        board = self.get_object_and_check_permissions(pk)
        serializer = BoardSerializer(board, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        board = self.get_object_and_check_permissions(pk)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)