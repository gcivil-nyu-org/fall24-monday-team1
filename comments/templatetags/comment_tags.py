from django import template
from comments.models import Comment
from comments.views import get_or_create_comment_board

register = template.Library()

@register.inclusion_tag('comments/comment_board_detail.html', takes_context=True)
def render_comment_board(context, identifier):
    root_comment = get_or_create_comment_board(identifier)
    comments = root_comment.replies.all() if root_comment else []
    return {
        'root_comment': root_comment,
        'comments': comments,
        'request': context['request'],
        'curPath': context['curPath'],
    }

@register.inclusion_tag('comments/review_board_detail.html', takes_context=True)
def render_review_board(context, identifier):
    root_comment = get_or_create_comment_board(identifier)
    comments = root_comment.replies.all() if root_comment else []
    return {
        'root_comment': root_comment,
        'comments': comments,
        'request': context['request'],
        'curPath': context['curPath'],
    }