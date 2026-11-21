from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        request.session['is_auth'] = True
        return redirect('questions:index')
    
    return render(request, 'core/login.html')

def logout_view(request):
    request.session.flush()
    return redirect('questions:index')

def signup_view(request):
    return render(request, 'core/register.html')

def profile_view(request):
    user = {'id': 0, 'name': 'Jack', 'surname': 'Skellingthon'}
    return render(request, 'core/settings.html', {
        'user': user,
    })
