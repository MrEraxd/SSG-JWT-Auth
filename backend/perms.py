# This is class that will test if user have required
# permission for this path, in the constructor we assign
# name of the required permission and then raise exception
# Before checking permission we will validate token to be
# sure it is not expired/modified
class PermissionChecker:
    def __init__(
        self,
        requierd_permission: str,
    ):
        self.fixed_content = requierd_permission

    def __call__(
        self,
        auth_token: Annotated[dict | None, Depends(validate_token)],
    ):
        print(auth_token)
        return False


# Get prodtected data
@app.get("/protected-data/")
async def orders(can_access: Annotated[bool, Depends(PermissionChecker(""))]):
    return {"superSecretData": "Hello, I'm secret"}
