from django.shortcuts import render, redirect


def chatPage(request, *args, **kwargs):
    return render(request, "app/chatPage.htm")


from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render , get_object_or_404

User = get_user_model()

@login_required
def users_list(request):
    users = User.objects.exclude(username=request.user.username)
    return render(request, 'app/index.htm', {'users': users})





@login_required
def private_chat_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    return render(request, 'app/private_chat.htm', {
        'other_user': other_user,
        'sender_id': request.user.id,  # ✅ Pass sender_id to template
        'request': request ,          # ✅ Optional: if you're using {{ request.user.username }} in JS
        'sender' : request.user.username
    })