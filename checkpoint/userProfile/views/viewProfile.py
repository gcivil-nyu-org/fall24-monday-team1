from django.http import HttpResponse

def viewProfile(request):
    return HttpResponse("u r viewing profile")