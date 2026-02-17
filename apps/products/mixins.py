from django.db import models
from django.utils.text import slugify
class SlugMixin(models.Model):
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        abstract = True

    def generate_slug(self, base):
        base_slug = slugify(base)
        slug = base_slug
        counter = 1
        ModelClass = self.__class__
        while ModelClass.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug
