class UsersController():
    async def read_users(self):
        return [{"text": "This is the users path"}]
    
    async def read_user(self, user_id: str):
        return [{"text": f"This is the user {user_id} path"}]