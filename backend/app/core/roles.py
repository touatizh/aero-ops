from app.models.user import Role

PILOT: tuple[Role, ...] = (Role.PI,)
OPS: tuple[Role, ...] = (Role.OPS,)
ADMIN: tuple[Role, ...] = (Role.ADMIN,)
PILOT_OR_OPS: tuple[Role, ...] = (Role.PI, Role.OPS)
OPS_OR_ADMIN: tuple[Role, ...] = (Role.OPS, Role.ADMIN)
ALL_ROLES: tuple[Role, ...] = tuple(Role)
