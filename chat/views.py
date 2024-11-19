from django.shortcuts import render, redirect


def chatPage(request,room_id):
    if not request.user.is_authenticated:
        return redirect("login")
    context = {
        "room_name": room_id,
    }
    return render(request, "chat/chatPage.html", context)