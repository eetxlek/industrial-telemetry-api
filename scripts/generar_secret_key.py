
import secrets

def generate_secret_key():
    """Genera una SECRET_KEY segura"""
    key = secrets.token_urlsafe(32)
    print("=" * 60)
    print("SECRET_KEY generada:")
    print(key)
    print("=" * 60)
    print("\nCopia esta clave a tu archivo .env:")
    print(f"SECRET_KEY={key}")
    print("=" * 60)

if __name__ == "__main__":
    generate_secret_key()