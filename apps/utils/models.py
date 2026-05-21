"""Django models utilities."""

# Django
from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    """Project base model.
        + created (DateTime): Store the datetime the object was created.
        + modified (DateTime): Store the last datetime the object was modified.
    """

    created = models.DateTimeField(
        'created at',
        auto_now_add=True,
        help_text='Date time on which the object was created.'
    )
    modified = models.DateTimeField(
        'modified at',
        auto_now=True,
        help_text='Date time on which the object was last modified.'
    )

    delete = models.DateTimeField(
        'delete at',
        null=True,
        blank=True,
        default=None,
        help_text='Date time on which the object was last delete.'
    )

    uc = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name="%(class)s_created",
        related_query_name="%(class)ss"
    )
    um = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name="%(class)s_update",
        related_query_name="%(class)ss"
    )

    def set_user(self, user):
        self.uc = user
        self.um = user

    class Meta:
        """Meta option."""

        abstract = True

        get_latest_by = 'created'
        ordering = ['-created', '-modified']
