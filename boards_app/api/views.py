from rest_framework import generics, permissions, status
from boards_app.models import Board
from .serializers import BoardSerializer, SingleBoardSerializer
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.views import APIView



class BoardCreateView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        serializer.save()



class BoardDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            board=Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found."}, status=status.HTTP_404_NOT_FOUND)
    
        serializer = SingleBoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        try:
            board = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BoardSerializer(board, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            board = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found."}, status=status.HTTP_404_NOT_FOUND)

        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)