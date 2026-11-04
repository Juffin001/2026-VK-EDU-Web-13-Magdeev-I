from django.shortcuts import render, redirect

# Заглушки для сайдбара
ALL_TAGS = [{'id': j, 'text': f'тег {j}'} for j in range(10)]
BEST_USERS = [{'id': j, 'text': f'пользователь {j}'} for j in range(10)]

def login_view(request):
    if request.method == 'POST':
        request.session['is_auth'] = True
        return redirect('questions:index')
    
    return render(request, 'core/login.html', {
        'tags': ALL_TAGS, 
        'best_users': BEST_USERS
    })

def logout_view(request):
    request.session.flush()
    return redirect('questions:index')

def signup_view(request):
    return render(request, 'core/register.html', {
        'tags': ALL_TAGS, 
        'best_users': BEST_USERS
    })

def profile_view(request):
    user = {'id': 0, 'name': 'Jack', 'surname': 'Skellingthon'}
    return render(request, 'core/settings.html', {
        'tags': ALL_TAGS, 
        'best_users': BEST_USERS,
        'user': user,
    })