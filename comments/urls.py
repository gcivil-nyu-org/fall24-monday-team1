from django.urls import path
from .views import (
    create_reply,
    edit_comment,
    delete_comment,
    test_comment_board,
    upvote_comment,
    downvote_comment,
)

urlpatterns = [
    path('reply/<int:parent_id>/', create_reply, name='create_reply'),
    path('edit/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('delete/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('test/', test_comment_board, name='comments_test'),
    path('upvote/<int:comment_id>/', upvote_comment, name='upvote_comment'),
    path('downvote/<int:comment_id>/', downvote_comment, name='downvote_comment'),
]