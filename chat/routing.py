from channels import include


project_routing = [
    include("rooms.routing.app_routing", path=r"^/ws"),
    include("users.routing.app_routing", path=r"^/ws"),
]