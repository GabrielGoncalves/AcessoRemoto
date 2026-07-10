import secrets
import string

class PasswordService:
    @staticmethod
    def generate_safe_password(length=32):
        safe_punctuation = "_-."
        
        alphabet = string.ascii_letters + string.digits + safe_punctuation
        
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            
            if (any(c.islower() for c in password) and
                any(c.isupper() for c in password) and
                any(c.isdigit() for c in password) and
                any(c in safe_punctuation for c in password) and
                password[0] in string.ascii_letters + string.digits):
                break
                
        return password