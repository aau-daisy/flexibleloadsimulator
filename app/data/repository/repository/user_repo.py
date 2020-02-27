import logging

from app.data.model.role_type_enum import RoleTypeEnum
from app.data.model.user import User
from app.data.model.user_role import Role

LOGGER = logging.getLogger(__name__)


def add_user(username, password, first_name, last_name, email, session):
    """

    Creates and saves a new user to the database

    :param session:
    :param username:
    :param password:
    :param first_name:
    :param last_name:
    :param email:
    :return: id of the new user
    """

    new_user = User(username, password, first_name, last_name, email)
    session.add(new_user)
    session.commit()

    return new_user


def find_user(session, user_id=None, serialize=False):
    """

    Fetches a single user or all users

    :param session:
    :param user_id: the user's id if need to return single user
    :param serialize: whether to return as dictionary or not
    :return: single user if id specified else all users
    """

    if user_id is None:
        users = session.query(User).order_by(User.first_name).all()
    else:
        users = session.query(User).filter(User.id == user_id).all()

    if serialize:
        return [user.serialize() for user in users]
    else:
        return users


def find_by_username(username, session):
    """

    Fetches a single user by name

    :param session:
    :param username:
    :return: a single user if found else None
    """

    users = session.query(User).filter(User.username == username).all()

    return users[0] if len(users) > 0 else None


def find_by_email(email, session):
    """

    Fetches a single user by email

    :param session:
    :param email:
    :return: a single user if found else None
    """

    users = session.query(User).filter(User.email == email).all()

    return users[0] if len(users) > 0 else None


def update_user(username, new_user, session):
    """

    Modify a user

    :param session:
    :param username: the user to be changed:
    :param new_user: the new user details as a dictionary
    :return: the updated user as dictionary
    """

    user = find_by_username(username, session)
    if user is None:
        return None

    user.email = new_user["email"]
    user.first_name = new_user["first_name"]
    user.last_name = new_user["last_name"]
    if new_user.has_key("password") and new_user['password'] is not None:
        user.set_password(new_user["password"])

    session.add(user)
    session.commit()

    updated_user = find_by_username(username, session)

    return updated_user


def delete_user(username, session):
    """

    Delete a user from the database

    :param session:
    :param username:
    :return: True if success else false
    """

    user = find_by_username(username, session)
    if user is None:
        return False

    user.devices = []
    session.commit()
    items_deleted = session.query(User).filter(User.username == username).delete()
    session.commit()

    return items_deleted > 0


def is_user_valid(username, password, session):
    """

    Check if user's credentials are valid

    :param session:
    :param username:
    :param password:
    :return: True if valid else False
    """

    user = find_by_username(username, session)
    return user.check_password(password) if user is not None else False


def get_user_devices(session, username, serialize=False):
    """

    get the list of devices for the current user

    :param session:
    :param username:
    :param serialize:
    :return list of devices for the given user:
    """

    user = find_by_username(username, session)

    LOGGER.debug("user name: %s, no of devices: %d" % (username, user.devices.count()))
    # user.devices[0]
    # user.devices.filter_by(load_id='some-id').count()

    if serialize:
        return [device.serialize() for device in user.devices] if user.devices.count() > 0 else []
    else:
        return user.devices


def add_role(username, role_name, session):
    """

    :param session:
    :param username:
    :param role_name:
    :return:
    """

    user = find_by_username(username, session)

    role = session.query(Role).filter(Role.name == RoleTypeEnum(role_name)).first()
    if role:
        user.roles.append(role)
    else:
        user.roles.append(Role(name=RoleTypeEnum(role_name)))
    session.commit()

    return user


def revoke_role(username, role_name, session):
    """

    :param session:
    :param username:
    :param role_name:
    :return:
    """

    user = find_by_username(username, session)

    role = session.query(Role).filter(Role.name == RoleTypeEnum(role_name)).first()
    if not role:
        return user

    user.roles.remove(role)
    session.commit()

    return user


def update_max_allowed_devices(username, new_max_allowed_devices, session):
    """

    :param username:
    :param new_max_allowed_devices:
    :param session:
    :return:
    """

    user = find_by_username(username, session)

    user.max_devices = new_max_allowed_devices
    session.commit()

    return user
