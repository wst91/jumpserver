from typing import Iterable
from enum import Enum
from collections import defaultdict

from .clients import WeCom


class BackendEnum(Enum):
    WECOM = WeCom


class UserUtils:
    def __init__(self, users):
        self._users = users

    def get_users(self, type_lower_name):
        method_name = f'get_{type_lower_name}_users'
        method = getattr(self, method_name)
        return method()

    def get_wecom_users(self):
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


class Message:

    def send_msg(self, data: dict, users: Iterable, backends: Iterable = BackendEnum):
        user_utils = UserUtils(users)
        failed_users_mapper = defaultdict(list)

        for backend in backends:
            backend: BackendEnum

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


    def get_default_msg(self):
        pass

    def get_wecom_msg(self):
        raise NotImplementedError

