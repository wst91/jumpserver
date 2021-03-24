from ..backends.wecom import WeCom


class Client:
    def __init__(self):
        self.wecom = WeCom()

    def send_msg(self, users, msg):
        return self.wecom.send_text(users, msg)
