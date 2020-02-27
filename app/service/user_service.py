import logging
from app.data.repository import user_repo
from app.data.database import session_scope

LOGGER = logging.getLogger(__name__)


class UserService:

    def __init__(self):

        self.user_repo = user_repo

        # Ensure that admin users exists
        with session_scope() as session:
            if self.user_repo.find_by_username("admin", session) is None:
                self.add_user("admin", "password", "Admin", "User", "admin@email.com", session)
                self.add_role("admin", "admin", session)
                self.add_role("admin", "developer", session)
                self.add_role("admin", "end-user", session)
            if self.user_repo.find_by_username("aau_foa", session) is None:
                self.add_user("aau_foa", "password", "AAU", "FOA", "aau_foa@email.com", session)
                self.update_max_allowed_devices("aau_foa", 5000, session)

    def add_user(self, username, password, first_name, last_name, email, session):
        """

        :param username:
        :param password:
        :param first_name:
        :param last_name:
        :param email:
        :param session:
        :return:
        """
        if self.user_repo.find_by_username(username, session) is not None:
            msg = {"msg": "error: username already taken"}
            return None, msg

        if self.user_repo.find_by_email(email, session) is not None:
            msg = {"msg": "error: another user already registered with the given email"}
            return None, msg

        user = self.user_repo.add_user(username, password, first_name, last_name, email, session)
        msg = {"msg": "success: user created"}
        return user, msg

    def update_user(self, old_user, new_user_dict, session):
        """

        :param old_user: the old user as instance of User class
        :param new_user_dict: the updated user info as dictionary
        :param session:
        :return: the updated user as instance of User class
        """

        if "first_name" not in new_user_dict.keys():
            new_user_dict.first_name = old_user.first_name
        if not new_user_dict.has_key("last_name"):
            new_user_dict.last_name = old_user.last_name

        # make sure that email not registered by another user
        if "email" not in new_user_dict.keys() or new_user_dict.email == old_user.email:
            new_user_dict.email = old_user.email
        else:
            if self.user_repo.find_by_email(new_user_dict.email, session) is not None:
                msg = {"msg": "error: another user already registered with the given email"}
                return None, msg

        updated_user = self.user_repo.update_user(old_user.username, new_user_dict, session)
        msg = {"msg": "success: user updated"}
        return updated_user, msg

    def update_max_allowed_devices(self, username, new_max_device_limit, session):
        """

        :param username: the username
        :param new_max_device_limit
        :param session:
        :return: the updated user as instance of User class
        """

        try:
            int(new_max_device_limit)
        except ValueError:
            msg = {"msg": "error: must provide non-negative (>=0) number"}
            return self.user_repo.find_by_username(self.user_repo, session), msg

        updated_user = self.user_repo.update_max_allowed_devices(username, new_max_device_limit, session)
        msg = {"msg": "success: max device limit set to " + str(new_max_device_limit) + " for " + username}
        return updated_user, msg

    @staticmethod
    def get_user(username, session):
        """

        get a user form db

        :param username:
        :param session:
        :return:
        """

        return user_repo.find_by_username(username, session)

    @staticmethod
    def get_all_users(session):
        """

        :param session:
        :return a list of all users:
        """
        return user_repo.find_user(session)

    def get_devices(self, username, session):
        """

        :param username:
        :param session:
        :return:
        """
        return self.user_repo.get_user_devices(session, username)

    def delete_user(self, username, session):
        """

        :param username:
        :param session:
        :return:
        """

        return self.user_repo.delete_user(username, session)

    def add_role(self, username, new_role, session):
        """

        :param username:
        :param new_role:
        :param session:
        :return:
        """

        return self.user_repo.add_role(username, new_role, session)

    def revoke_role(self, username, role_name, session):
        """

        :param username:
        :param role_name:
        :param session:
        :return:
        """

        return self.user_repo.revoke_role(username, role_name, session)

    def is_user_valid(self, username, password, session):
        """

        :param username:
        :param password:
        :param session:
        :return: True if valid username and password
        """

        return self.user_repo.is_user_valid(username, password, session)
