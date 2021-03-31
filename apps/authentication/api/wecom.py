from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from users.utils import is_auth_password_time_valid
from users.models import User
from common.utils import get_logger
from common.permissions import IsOrgAdmin
from common.mixins.api import RoleUserMixin, RoleAdminMixin
from authentication import errors

logger = get_logger(__file__)


class WeComQRUnBindBase(APIView):
    user: User

    def post(self, request: Request):
        if not is_auth_password_time_valid(request.session):
            raise PermissionDenied

        user = self.user

        if not user.wecom_id:
            raise errors.WeComNotBound

        user.wecom_id = ''
        user.save()
        return Response()


class WeComQRUnBindForUserApi(RoleUserMixin, WeComQRUnBindBase):
    permission_classes = (IsAuthenticated,)


class WeComQRUnBindForAdminApi(RoleAdminMixin, WeComQRUnBindBase):
    permission_classes = (IsOrgAdmin,)
