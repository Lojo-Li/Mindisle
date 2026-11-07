# -*- coding: utf-8 -*-
"""
Reset user password - Simple version
Usage: python reset_user_password.py
"""
import pymysql
import bcrypt
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'soulstation',
    'charset': 'utf8mb4'
}


def reset_user_password():
    """Reset user password to 123456"""
    connection = None
    try:
        print("="*60)
        print("Reset User Password")
        print("="*60)

        # Connect to database
        print("\nConnecting to database...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Check current user
        print("\nChecking current user info...")
        cursor.execute(
            "SELECT id, email, nickname, role, password_hash FROM users WHERE email = %s",
            ("test@example.com",)
        )
        result = cursor.fetchone()

        if not result:
            print("[ERROR] User test@example.com not found")
            return False

        user_id, email, nickname, role, old_hash = result
        print(f"\nCurrent user info:")
        print(f"  ID: {user_id}")
        print(f"  Email: {email}")
        print(f"  Role: {role}")
        print(f"  Old password hash: {old_hash[:50]}...")

        # Generate new password hash using bcrypt
        new_password = "123456"
        print(f"\nGenerating new password hash for: {new_password}")

        # Convert password to bytes and hash
        password_bytes = new_password.encode('utf-8')
        salt = bcrypt.gensalt()
        new_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

        print(f"  New hash: {new_hash[:50]}...")

        # Update password
        print(f"\nUpdating password...")
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (new_hash, "test@example.com")
        )
        connection.commit()

        print(f"[OK] Password updated successfully")

        # Verify update
        cursor.execute(
            "SELECT password_hash FROM users WHERE email = %s",
            ("test@example.com",)
        )
        verify_hash = cursor.fetchone()[0]
        print(f"Verification: New hash in database: {verify_hash[:50]}...")

        # Test password verification
        print(f"\nTesting password verification...")
        is_valid = bcrypt.checkpw(password_bytes, verify_hash.encode('utf-8'))
        print(f"Password verification result: {is_valid}")

        if is_valid:
            print("\n" + "="*60)
            print("SUCCESS! Password reset completed!")
            print("="*60)
            print("\nYou can now login with:")
            print("  Email: test@example.com")
            print("  Password: 123456")
            print("  Role: counselor")
            return True
        else:
            print("\n[ERROR] Password verification failed")
            return False

    except Exception as e:
        print(f"\n[ERROR] Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if connection:
            connection.close()
            print("\nDatabase connection closed")


if __name__ == "__main__":
    success = reset_user_password()
    sys.exit(0 if success else 1)
