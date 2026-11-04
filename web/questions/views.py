from django.shortcuts import render
from .utils import paginate

QUESTION_LIST = [
    {
        'id': i,
        'title': f'Title {i}',
        'text': f'Text {i}' * 10,
        'votes': f'{i+1}',
        'cnt_ans': f'{i+2}',
        'tags': [{'id': j, 'text': f'тег {j}'} for j in range(3)],
        'answers': [{'id': j, 'text': f'ответ на вопрос {i} номер {j}', 'is_correct': 0, 'votes': f'{j + 3}'} for j in range(5)]
    }
    for i in range(100)
]

for i in QUESTION_LIST:
    i['answers'][0]['is_correct'] = 1

ALL_TAGS = [{'id': j, 'text': f'тег {j}'} for j in range(10)]
BEST_USERS = [{'id': j, 'text': f'пользователь {j}'} for j in range(10)]

def index(request):
    page = paginate(QUESTION_LIST, request, per_page=5)

    return render(request, 'questions/index.html', {
        'questions': page,
        'page_obj': page,
        'tags': ALL_TAGS,
        'best_users': BEST_USERS
    })

def hot(request):
    page = paginate(QUESTION_LIST[::-1], request, per_page=5)

    return render(request, 'questions/index.html', {
        'questions': page,
        'page_obj': page,
        'tags': ALL_TAGS, 
        'best_users': BEST_USERS
    })

def ask(request):
    return render(request, 'questions/ask.html', {'tags': ALL_TAGS, 'best_users': BEST_USERS})

def question(request):
    question_id = request.GET.get('id') 
    if question_id and question_id.isdigit():
        question_data = next((q for q in QUESTION_LIST if q['id'] == int(question_id)), None)
    else:
        question_data = None
    return render(request, 'questions/question.html', {
        'question': question_data,
        'tags': ALL_TAGS,
        'best_users': BEST_USERS,
    })

def tag(request):
    page = paginate(QUESTION_LIST[::4], request, per_page=5)
    tag_id = request.GET.get('id')

    if tag_id and tag_id.isdigit():
        tag_data = next((q for q in ALL_TAGS if q['id'] == int(tag_id)), None)
    else:
        tag_data = None
    return render(request, 'questions/tag.html', {
        'questions': page,
        'page_obj': page,
        'tag': tag_data,
        'tags': ALL_TAGS,
        'best_users': BEST_USERS,
    })
