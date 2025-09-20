from passlib.context import CryptContext


class Hash:
    """
    Utility class for password hashing and verification using bcrypt.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        :param plain_password: The plain text password to verify.
        :param hashed_password: The hashed password for comparison.
        :return: True if the password matches, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hash a plain password.

        :param password: The plain text password to hash.
        :return: The hashed password.
        """
        return self.pwd_context.hash(password)
