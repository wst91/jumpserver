from django.utils.translation import gettext_lazy as _

from notifications.notifications import Message
from terminal.models import Command


class CommandExecutionAlert(Message):
    app_name = 'terminal'
    message = 'command_execution_alert'

    def get_email_msg(self, data):
        subject = _("Insecure Web Command Execution Alert: [%(name)s]") % {
            'name': data['user'],
        }
        input = data['input']
        input = input.replace('\n', '<br>')

        assets = ', '.join([str(asset) for asset in data['assets']])
        message = _("""
                <br>
                Assets: %(assets)s
                <br>
                User: %(user)s
                <br>
                Level: %(risk_level)s
                <br>

                ----------------- Commands ---------------- <br>
                %(command)s <br>
                ----------------- Commands ---------------- <br>
                """) % {
            'command': input,
            'assets': assets,
            'user': data['user'],
            'risk_level': Command.get_risk_level_str(data['risk_level']),
        }

        return {
            'subject': subject,
            'message': message
        }
