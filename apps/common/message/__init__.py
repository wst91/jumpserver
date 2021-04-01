from typing import Iterable
from enum import Enum

from .clients import WeCom


class BackendEnum(Enum):
    WECOM = WeCom


class UserUtils:
    def __init__(self, users: Iterable):
        self._users = users

    def


class Message:

    def send_msg(self, data: dict, users: Iterable, backends: Iterable = BackendEnum):

        for backend in backends:
            backend: BackendEnum

            lower_name = backend.name.lower()
            get_msg_method_name = f'get_{lower_name}_msg'
            get_msg_method = getattr(self, get_msg_method_name, self.get_default_msg)
            msg = get_msg_method(data)
            client = backend.value()
            client.send_msg(users, **msg)

    def get_default_msg(self):
        pass

    def get_wecom_msg(self):
        raise NotImplementedError

