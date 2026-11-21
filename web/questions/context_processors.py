from core.models import Profile

from .models import Tag


def sidebar(request):
    return {
        "popular_tags": Tag.objects.popular()[:20],
        "best_users": Profile.objects.by_rating().values_list("user__username", flat=True)[:10],
    }
