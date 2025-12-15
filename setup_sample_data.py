import hashlib
from db import get_connection

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()

def setup_sample_data():
    """Create tables and insert sample data into the meal planner SQLite database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create users table if not exists (SQLite syntax)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()
        print("✓ Users table created/verified")
        
        # Sample users (password: "password123")
        sample_users = [
            ("john_doe", "john@example.com"),
            ("jane_smith", "jane@example.com"),
            ("test_user", "test@example.com"),
        ]
        
        # Insert sample users
        for username, email in sample_users:
            pw_hash = hash_password("password123")
            try:
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, pw_hash),
                )
                conn.commit()
                print(f"✓ Added user: {username} (email: {email}, password: password123)")
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    print(f"⚠ User '{username}' already exists, skipping")
                else:
                    raise
        
        # Create meal_plans table (optional, for future use)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS meal_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                week_start DATE NOT NULL,
                budget REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        conn.commit()
        print("✓ Meal plans table created/verified")
        
        cursor.close()
        conn.close()
        
        print("\n✓ Sample data setup complete!")
        print("\nTest credentials:")
        print("  Username: john_doe")
        print("  Password: password123")
        
    except Exception as e:
        print(f"✗ Error setting up sample data: {e}")

if __name__ == "__main__":
    setup_sample_data()
