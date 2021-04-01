from django.db import models

from orgs.mixins.models import OrgModelMixin


class Subscription(OrgModelMixin, models.Model):
    users = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, related_name='subscriptions', db_constraint=False)
    groups = models.ForeignKey('users.UserGroup', on_delete=models.DO_NOTHING, related_name='subscriptions', db_constraint=False)
    message = models.CharField(max_length=128, default='', db_index=True)
    receive_backends_str = models.CharField(max_length=256, default='')

    @property
    def receive_backends(self):
        backends = self.receive_backends_str.split('|')
        return backends

    @receive_backends.setter
    def receive_backends(self, backends):
        backends_str = '|'.join(backends)
        self.receive_backends_str = backends_str
