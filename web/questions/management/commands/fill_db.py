import random
from collections import Counter
from itertools import batched
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.test.utils import override_settings
from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag


BATCH_SIZE = 1000


def save_posts_with_votes(model, posts, vote_counts, voter_ids, like_model, target_field, ratings):
    likes = []
    for post, count in zip(posts, vote_counts, strict=True):
        for user_id in random.sample(voter_ids, count):
            value = random.choice((-1, 1))
            post.votes += value
            likes.append(like_model(user_id=user_id, value=value, **{target_field: post}))
        ratings[post.author_id] += post.votes

    # Сначала публикации получают PK, затем Django может вставить связанные оценки.
    model.objects.bulk_create(posts, batch_size=BATCH_SIZE)
    like_model.objects.bulk_create(likes, batch_size=BATCH_SIZE)


class Command(BaseCommand):
    help = "Добавляет тестовых пользователей, вопросы, ответы, теги и оценки."

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, help="Количество новых пользователей и тегов")

    @transaction.atomic
    def handle(self, *args, ratio, **options):
        if ratio < 1:
            raise CommandError("Коэффициент должен быть положительным.")

        user_model = get_user_model()
        voter_ids = []
        if ratio == 1:
            # На пустой базе один пользователь может оценить лишь 10 + 100 публикаций.
            previous = user_model.objects.filter(username__startswith="filldb_").first()
            if previous is None:
                raise CommandError("Для первого запуска укажи ratio не меньше 2: для 200 разных голосов нужны два тестовых пользователя.")
            voter_ids.append(previous.pk)

        fake = Faker("ru_RU")
        run_id = uuid4().hex[:12]
        user_ids = []
        tag_ids = []
        question_ids = []
        ratings = Counter()

        # При DEBUG=True Django запоминает SQL со всеми значениями массовых вставок.
        with override_settings(DEBUG=False):
            for indices in batched(range(ratio), BATCH_SIZE):
                users = []
                tags = []
                for i in indices:
                    username = f"filldb_{run_id}_{i}"
                    user = user_model(
                        username=username, email=f"{username}@example.org",
                        first_name=fake.first_name(), last_name=fake.last_name(),
                    )
                    user.set_unusable_password()
                    users.append(user)
                    tags.append(Tag(text=f"{fake.word()[:25]}-{run_id}-{i}"))
                user_ids.extend(user.pk for user in user_model.objects.bulk_create(users))
                tag_ids.extend(tag.pk for tag in Tag.objects.bulk_create(tags))

            voter_ids.extend(user_ids)
            votes_per_question = min(10, len(voter_ids))
            answer_count = 100 * ratio
            remaining_votes = 200 * ratio - votes_per_question * 10 * ratio
            votes_per_answer, extra_votes = divmod(remaining_votes, answer_count)

            for indices in batched(range(10 * ratio), BATCH_SIZE):
                questions = [
                    Question(author_id=random.choice(user_ids), title=fake.sentence()[:150],
                             text=fake.paragraph())
                    for _ in indices
                ]
                save_posts_with_votes(Question, questions, [votes_per_question] * len(questions),
                                      voter_ids, QuestionLike, "question", ratings)
                links = []
                for question in questions:
                    question_ids.append(question.pk)
                    count = random.randint(1, min(3, len(tag_ids)))
                    for tag_id in random.sample(tag_ids, count):
                        links.append(Question.tags.through(question_id=question.pk, tag_id=tag_id))
                Question.tags.through.objects.bulk_create(links, batch_size=BATCH_SIZE)

            accepted = set()
            for indices in batched(range(answer_count), BATCH_SIZE):
                answers = []
                counts = []
                for i in indices:
                    # Первый вопрос демонстрирует пагинацию, последний остаётся без ответов.
                    question_id = question_ids[0] if i < 31 else question_ids[random.randrange(len(question_ids) - 1)]
                    is_correct = question_id not in accepted and random.random() < 0.1
                    if is_correct:
                        accepted.add(question_id)
                    answers.append(Answer(question_id=question_id, author_id=random.choice(user_ids),
                                          text=fake.sentence(), is_correct=is_correct))
                    counts.append(votes_per_answer + (i < extra_votes))
                save_posts_with_votes(Answer, answers, counts, voter_ids, AnswerLike, "answer", ratings)

            for ids in batched(user_ids, BATCH_SIZE):
                Profile.objects.bulk_create([Profile(user_id=pk, rating=ratings[pk]) for pk in ids])

        self.stdout.write(self.style.SUCCESS(
            f"Добавлено пользователей и профилей: по {ratio}, тегов: {ratio}, "
            f"вопросов: {10 * ratio}, ответов: {answer_count}, оценок: {200 * ratio}."
        ))
