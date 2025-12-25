import os
from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.utils.translation import gettext_lazy as _

from bugsink.decorators import atomic_for_request_method

from .models import AuthToken


@atomic_for_request_method
@user_passes_test(lambda u: u.is_superuser)
def auth_token_list(request):
    auth_tokens = AuthToken.objects.all()

    if request.method == 'POST':
        # DIT KOMT ZO WEL
        full_action_str = request.POST.get('action')
        action, pk = full_action_str.split(":", 1)
        if action == "delete":
            AuthToken.objects.get(pk=pk).delete()

            messages.success(request, _('Token deleted'))
            return redirect('auth_token_list')

    return render(request, 'bsmain/auth_token_list.html', {
        'auth_tokens': auth_tokens,
    })

"""
@atomic_for_request_method
@user_passes_test(lambda u: u.is_superuser)
def auth_token_create(request):
    if request.method != 'POST':
        raise Http404("Invalid request method")

    auth_token = AuthToken.objects.create()
    try:
        # logic views.py -> bsmain -> bugsink -> issues -> token.txt
        current_file_path = os.path.abspath(__file__)
        bsmain_dir = os.path.dirname(current_file_path) # get bsmain path
        project_root = os.path.dirname(bsmain_dir)       # bugsink project root directory
        
        target_file_path = os.path.join(project_root, 'issues', 'token.txt')

        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

        with open(target_file_path, 'a', encoding='utf-8') as f:
            f.write(f"{auth_token.token}\n")

        messages.info(request, f"Token saved to {target_file_path}")

    except (PermissionError, OSError, IOError) as e:
        error_msg = f"Token created, but failed to write to file: {str(e)}"
        messages.warning(request, error_msg)
    return redirect("auth_token_list")
"""