from django.contrib.auth.mixins import UserPassesTestMixin
from account.models import UserType


class HasAdminAccessPermission(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.type in [UserType.admin.value, UserType.superuser.value]
        return False


class HasCustomerAccessPermission(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.type == UserType.customer.value
        return False