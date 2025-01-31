from django.utils.timezone import now


def get_post_info(post_model):
    res = post_model.objects.select_related(
        'category',
        'location',
        'author'
    ).filter(
        is_published=True,
        pub_date__lt=now(),
        category__is_published=True
    )
    return res


def detailed_post_permission(self):
    permission = (
        (self.request.user == self.get_object().author
         ) or (
            (self.get_object().is_published)
            and (self.get_object().category.is_published)
            and (self.get_object().pub_date <= now())
        )
    )
    return permission
