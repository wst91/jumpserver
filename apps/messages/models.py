from django.db import models

from orgs.mixins.models import OrgModelMixin


class Subscription(OrgModelMixin, models.Model):
    users = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, related_name='subscriptions', db_constraint=False)
    groups = models.ForeignKey('users.UserGroup', on_delete=models.DO_NOTHING, related_name='subscriptions', db_constraint=False)
    message = models.CharField(max_length=64)

