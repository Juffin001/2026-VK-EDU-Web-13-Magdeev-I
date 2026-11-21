from django.core.paginator import Paginator

from .models import Answer


def paginate(objects_list, request, per_page=5):
    paginator = Paginator(objects_list, per_page)
    page = paginator.get_page(request.GET.get("page"))
    first = max(1, page.number - 2)
    last = min(paginator.num_pages, page.number + 2)
    page.visible_numbers = range(first, last + 1)
    return page


def paginate_questions(questions, request):
    page = paginate(questions, request, per_page=20)
    cards = list(page.object_list.prefetch_related("tags"))
    counts = Answer.objects.counts_for_questions([question.pk for question in cards])
    for question in cards:
        question.cnt_ans = counts.get(question.pk, 0)
    page.object_list = cards
    return page
