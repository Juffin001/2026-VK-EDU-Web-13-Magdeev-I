from django.shortcuts import render, get_object_or_404
from .utils import paginate, paginate_questions
from .models import Question, Tag, Answer

def index(request):
    page = paginate_questions(Question.objects.new(), request)

    return render(request, 'questions/index.html', {
        'questions': page,
        'page_obj': page,
    })

def hot(request):
    page = paginate_questions(Question.objects.hot(), request)

    return render(request, 'questions/index.html', {
        'questions': page,
        'page_obj': page,
    })

def ask(request):
    return render(request, 'questions/ask.html')

def question(request, pk):
    current_question = get_object_or_404(Question, pk=pk)
    answers = Answer.objects.for_question(current_question)
    page = paginate(answers, request, per_page=30)

    return render(request, "questions/question.html", {
        "question": current_question,
        "page_obj": page,
    })

def tag(request, tag_text):
    current_tag = get_object_or_404(Tag, text=tag_text)
    page = paginate_questions(Question.objects.by_tag(current_tag), request)

    return render(request, "questions/tag.html", {
        "tag": current_tag,
        "questions": page,
        "page_obj": page,
    })
