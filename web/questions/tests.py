from django.contrib.auth import get_user_model
from django.db import connection
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.test.utils import CaptureQueriesContext

from .models import Answer, Question, Tag
from .utils import paginate, paginate_questions


class PaginationTests(SimpleTestCase):
    def test_navigation_on_a_large_feed(self):
        for value, current, numbers in [
            ("abc", 1, [1, 2, 3]),
            ("2500", 2500, [2498, 2499, 2500, 2501, 2502]),
            ("99999", 5000, [4998, 4999, 5000]),
        ]:
            with self.subTest(value=value):
                request = RequestFactory().get("/", {"page": value, "sort": "new"})
                page = paginate(range(100000), request, per_page=20)
                self.assertEqual(page.number, current)
                self.assertEqual(list(page.visible_numbers), numbers)
                html = render_to_string(
                    "questions/partials/footer_with_pagination.html", {"page_obj": page}, request
                )
                self.assertInHTML(
                    f'<span class="pagination-link pagination-link-active" aria-current="page">{current}</span>',
                    html,
                )
                self.assertEqual("Предыдущая страница" in html, page.has_previous())
                self.assertEqual("Следующая страница" in html, page.has_next())
                self.assertIn("sort=new", html)


class QuestionCardTests(TestCase):
    def test_second_page_counts_answers_and_loads_tags_in_bulk(self):
        user = get_user_model().objects.create_user("author")
        questions = Question.objects.bulk_create([
            Question(title=f"Вопрос {i}", text="Текст", author=user) for i in range(22)
        ])
        tag = Tag.objects.create(text="python")
        questions[1].tags.add(tag)
        for q in (questions[1], questions[1], questions[-1]):
            Answer.objects.create(question=q, author=user, text="Ответ")

        request = RequestFactory().get("/", {"page": 2})
        with CaptureQueriesContext(connection) as queries:
            page = paginate_questions(Question.objects.new(), request)
            cards = [(q.pk, q.cnt_ans, list(q.tags.all())) for q in page]

        self.assertEqual(cards, [(questions[1].pk, 2, [tag]), (questions[0].pk, 0, [])])
        self.assertEqual(len(queries), 4)  # Число вопросов, карточки, теги, счётчики ответов.
        self.assertNotIn("JOIN", queries[0]["sql"].upper())
