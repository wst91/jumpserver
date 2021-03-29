from django.conf import settings

from ..backends.wecom import WeCom


class Client:
    def __init__(self):
        self.wecom = WeCom(
            corpid=settings.WECOM_CORPID,
            corpsecret=settings.WECOM_CORPSECRET,
            agentid=settings.WECOM_AGENTID
        )

    def send_msg(self, users, msg):
        return self.wecom.send_text(users, msg)
