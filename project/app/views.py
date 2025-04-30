from django.shortcuts import render, redirect


def chatPage(request, *args, **kwargs):
    # if not request.user.is_authenticated:
    #     return redirect("login-user")
    # context = {}
    return render(request, "app/chatPage.htm")


from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render , get_object_or_404

User = get_user_model()

@login_required
def users_list(request):
    users = User.objects.exclude(username=request.user.username)
    return render(request, 'app/index.htm', {'users': users})




def private_chat(request, username):
    other_user = get_object_or_404(User, username=username)
    return render(request, "app/private_chat.htm", {
        "other_user": other_user,
    })