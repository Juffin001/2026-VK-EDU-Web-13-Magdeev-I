from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.urls import reverse
from django.utils.text import Truncator

from .models import (
    Answer,
    AnswerLike,
    Question,
    QuestionLike,
    Tag,
)


class AnswerAuthorWidget(ForeignKeyRawIdWidget):
    author = None

    def label_and_url_for_value(self, value):
        # При изменении автора в форме подпись должна соответствовать новому ID.
        if self.author is None or str(value) != str(self.author.pk):
            return super().label_and_url_for_value(value)
        opts = self.author._meta
        url = reverse(
            f"{self.admin_site.name}:{opts.app_label}_{opts.model_name}_change",
            args=[self.author.pk],
        )
        return Truncator(self.author).words(14), url


class AnswerInlineForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = "__all__"
        widgets = {
            "author": AnswerAuthorWidget(Answer._meta.get_field("author").remote_field, admin.site),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.author_id and "author" in self.fields:
            self.fields["author"].widget.author = self.instance.author


class AnswerInline(admin.TabularInline):
    model = Answer
    form = AnswerInlineForm
    extra = 0
    raw_id_fields = ("author",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "votes", "created_at")
    search_fields = ("title", "author__username")
    list_filter = ("is_active", "created_at")
    list_select_related = ("author",)
    raw_id_fields = ("author", "tags")
    inlines = (AnswerInline,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("text", "is_active", "created_at")
    search_fields = ("text",)
    list_filter = ("is_active", "created_at")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "author", "votes", "is_correct")
    search_fields = ("text", "question__title", "author__username")
    list_filter = ("is_correct", "created_at")
    list_select_related = ("question", "author")
    raw_id_fields = ("question", "author")


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "value")
    search_fields = ("user__username", "question__title")
    list_filter = ("value", "created_at")
    list_select_related = ("user", "question")
    raw_id_fields = ("user", "question")


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "answer", "value")
    search_fields = ("user__username", "answer__text")
    list_filter = ("value", "created_at")
    list_select_related = ("user", "answer")
    raw_id_fields = ("user", "answer")
