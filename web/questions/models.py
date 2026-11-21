from django.db import models
from django.contrib import auth
from django.conf import settings
from django.urls import reverse

User = auth.get_user_model()

class DefaultModel(models.Model):
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        abstract = True

class QuestionQuerySet(models.QuerySet):
    def new(self):
        return self.order_by("-created_at", "-pk")

    def hot(self):
        return self.order_by("-votes", "-created_at", "-pk")

    def by_tag(self, tag):
        return self.filter(tags=tag).hot()

class Question(DefaultModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Автор вопроса", on_delete=models.SET_NULL, null=True,related_name="questions")
    title = models.TextField(max_length=150, verbose_name="Заголовок вопроса")
    text = models.TextField(max_length=3000, verbose_name="Текст вопроса")
    votes = models.IntegerField(verbose_name="Рейтинг", default=0)
    tags = models.ManyToManyField("Tag", related_name="questions", blank=True, verbose_name="Теги")
    objects = QuestionQuerySet.as_manager()

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
    def __str__(self):
        return f"Заголовок вопроса: {self.title}"
    def get_absolute_url(self):
        return reverse("questions:question", kwargs={"pk": self.pk})


class TagQuerySet(models.QuerySet):
    def popular(self):
        return (
            self.annotate(question_count=models.Count("questions"))
            .filter(question_count__gt=0)
            .order_by("-question_count", "text")
        )


class Tag(DefaultModel):
    objects = TagQuerySet.as_manager()
    text = models.TextField(max_length=50,unique=True, verbose_name="Название тега")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return f"Тег: {self.text}"

    def get_absolute_url(self):
        return reverse("questions:tag", kwargs={"tag_text": self.text})

class AnswerQuerySet(models.QuerySet):
    def counts_for_questions(self, question_ids):
        return dict(
            self.filter(question_id__in=question_ids)
            .values("question_id")
            .annotate(total=models.Count("*"))
            .values_list("question_id", "total")
        )

    def for_question(self, question):
        return self.filter(question=question).order_by(
            "-votes", "-created_at", "-pk"
        )

class Answer(DefaultModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Автор ответа", on_delete=models.CASCADE,related_name="answers")
    question = models.ForeignKey(Question, verbose_name="Вопрос", on_delete=models.CASCADE,related_name="answers")
    text = models.TextField(max_length=3000, verbose_name="Текст ответа")
    votes = models.IntegerField(verbose_name="Рейтинг", default=0)
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ?")

    objects = AnswerQuerySet.as_manager()

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return f"Ответ: {self.text[:80]}"

class QuestionLike(DefaultModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Пользователь", on_delete=models.CASCADE,related_name="questionlikes")
    question = models.ForeignKey(Question, verbose_name="Вопрос", on_delete=models.CASCADE,related_name="questionlikes")
    value = models.IntegerField(verbose_name="Оценка", choices=[(1, "За"), (-1, "Против")])
    class Meta:
        verbose_name = "Оценка вопроса"
        verbose_name_plural = "Оценки вопросов"
        unique_together = [("user", "question")]

    def __str__(self):
        return f"Оценка вопроса №{self.question_id} пользователем №{self.user_id}: {self.value}"

class AnswerLike(DefaultModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Пользователь", on_delete=models.CASCADE,related_name="answerlikes")
    answer = models.ForeignKey(Answer, verbose_name="Ответ", on_delete=models.CASCADE,related_name="answerlikes")
    value = models.IntegerField(verbose_name="Оценка", choices=[(1, "За"), (-1, "Против")],)
    class Meta:
        verbose_name = "Оценка ответа"
        verbose_name_plural = "Оценки ответов"
        unique_together = [("user", "answer")]

    def __str__(self):
        return f"Оценка ответа №{self.answer_id} пользователем №{self.user_id}: {self.value}"
