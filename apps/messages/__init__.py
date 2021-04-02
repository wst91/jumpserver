from typing import Iterable
from collections import defaultdict

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from .backends.wecom import WeCom
from .backends.email import Email
from .models import Subscription


class BackendChoices(TextChoices):
    WECOM = 'wecom', _('WeCom')
    EMAIL = 'email', _('Email')

    client_mapper = {
        WECOM: WeCom,
        EMAIL: Email
    }

    @property
    def client(self):
        client = self.client_mapper[self]
        return client


class UserUtils:
    def __init__(self, users):
        self._users = users

    def get_users(self, type_lower_name):
        method_name = f'get_{type_lower_name}_accounts'
        method = getattr(self, method_name)
        return method()

    def get_wecom_accounts(self):
        users = []
        unbound_users = []
        wecomid_user_mapper = {}

        for user in self._users:
            if user.wecom_id:
                wecomid_user_mapper[user.wecom_id] = user
                users.append(user.wecom_id)
            else:
                unbound_users.append(user)
        return users, unbound_users, wecomid_user_mapper

    def get_email_accounts(self):
        pass


class Message:

    app_name: str
    message: str

    def publish(self, data: dict):
        backend_user_mapper = defaultdict(list)
        subscriptions = Subscription.objects.filter(
            app_name=self.app_name,
            message=self.message
        ).prefetch_related('user')

    def send_msg(self, data: dict, users: Iterable, backends: Iterable = BackendChoices):
        user_utils = UserUtils(users)
        failed_users_mapper = defaultdict(list)

        for backend in backends:
            backend: BackendChoices

            lower_name = backend.name.lower()
            user_accounts, invalid_users, account_user_mapper = user_utils.get_users(lower_name)
            get_msg_method_name = f'get_{lower_name}_msg'
            get_msg_method = getattr(self, get_msg_method_name, self.get_default_msg)
            msg = get_msg_method(data)
            client = backend.value()
            failed_users = client.send_msg(user_accounts, **msg)

            for u in failed_users:
                invalid_users.append(account_user_mapper[u])

            failed_users_mapper[backend] = invalid_users

        return failed_users_mapper

    def get_default_msg(self, data):
        pass

    def get_wecom_msg(self, data):
        raise NotImplementedError

    def get_email_msg(self, data):
        raise NotImplementedError
