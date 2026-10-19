from models.user import User

class UserAuthService:
    @staticmethod
    def create_token(user):
        return str(user.get_id()) + ':' + user.get_auth_token()
    
    @staticmethod
    def get_user_by_token(token):
        if token == '':
            return None

        [user_id,_auth_token] = token.split(':',2)
        user = User.get_by_id(int(user_id))
        
        if user is None:
            return None
        if user.get_auth_token() != _auth_token:
            return None
        return user