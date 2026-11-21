from django.db import models
from django.conf import settings

class ProfileQuerySet(models.QuerySet):
    def by_rating(self):
        return self.order_by("-rating", "user__username")


class Profile(models.Model):
    objects = ProfileQuerySet.as_manager()

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="avatars/",
        blank=True,
    )
    rating = models.IntegerField(
        verbose_name="Рейтинг",
        default=0,
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль пользователя {self.user.get_username()}"
