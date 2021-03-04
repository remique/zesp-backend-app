from .users import UserApi, UsersApi, LoginApi, ProtectedApi
from .institutions import InstitutionsApi, InstitutionApi
from .roles import RolesApi, RoleApi, UserRoleApi, UserRolesApi
from .groups import GroupApi, GroupsApi, UserGroupsApi, UserGroupApi


def initialize_routes(api):
    api.add_resource(UsersApi, '/user')
    api.add_resource(UserApi, '/user/<id>')

    api.add_resource(InstitutionsApi, '/institution')
    api.add_resource(InstitutionApi, '/institution/<id>')

    api.add_resource(RolesApi, '/role')
    api.add_resource(RoleApi, '/role/<id>')
    api.add_resource(UserRolesApi, '/userrole/<userid>')
    api.add_resource(UserRoleApi, '/userrole')

    api.add_resource(GroupsApi, '/group')
    api.add_resource(GroupApi, '/group/<id>')
    api.add_resource(UserGroupsApi, '/usergroup/<userid>')
    api.add_resource(UserGroupApi, '/usergroup')

    api.add_resource(LoginApi, '/login')
    api.add_resource(ProtectedApi, '/protected')
