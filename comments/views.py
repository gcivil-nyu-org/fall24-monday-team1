from datetime import timezone
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from .models import Comment
from django.contrib.auth.decorators import login_required

# Create your views here.

from django.db import transaction

def get_or_create_comment_board(identifier):
    with transaction.atomic():
        # Try to get the existing root comment based on the identifier
        root_comment, created = Comment.objects.get_or_create(
            content=identifier,  # Use the identifier as content
            is_root=True,
            defaults={'author': None}  # Set defaults for a new root comment
        )
        return root_comment
    
def test_comment_board(request):
    context = {
        'curPath' : '/comments/test/',
    }
    return render(request, 'comments/test_comment_board.html', context=context)

@login_required
def create_reply(request, parent_id):
    parent_comment = get_object_or_404(Comment, id=parent_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        curPath = request.POST.get('curPath')  # Get curPath from the form data
        reply = Comment(author=request.user, content=content, parent=parent_comment)
        reply.save()
        print("Redirecting: " + curPath)
        return redirect(curPath)  # Redirect to curPath
    
    return HttpResponseNotFound("Page not found.")

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Check if the current user is the author of the comment
    if request.user != comment.author:
        return HttpResponseForbidden("You are not allowed to edit this comment.")

    if request.method == 'POST':
        comment.content = request.POST.get('content')
        comment.edited_at = timezone.now()  # Update the edited_at timestamp
        comment.save()
        curPath = request.POST.get('curPath')
        return redirect(curPath)
    
    return HttpResponseNotFound("Page not found.")

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Check if the current user is the author of the comment
    if request.user != comment.author:
        return HttpResponseForbidden("You are not allowed to delete this comment.")

    if request.method == 'POST':
        comment.delete()
        curPath = request.POST.get('curPath')
        return redirect(curPath)
    
    return HttpResponseNotFound("Page not found.")

@login_required
def upvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.downvote.all():
        comment.downvote.remove(request.user)
    if request.user not in comment.upvote.all():
        comment.upvote.add(request.user)
    else:
        comment.upvote.remove(request.user)
    curPath = request.POST.get('curPath')
    return redirect(curPath)

@login_required
def downvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.upvote.all():
        comment.upvote.remove(request.user)
    if request.user not in comment.downvote.all():
        comment.downvote.add(request.user)
    else:
        comment.downvote.remove(request.user)
    curPath = request.POST.get('curPath')
    return redirect(curPath)