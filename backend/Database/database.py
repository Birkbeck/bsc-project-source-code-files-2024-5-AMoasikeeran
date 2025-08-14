from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import hashlib
import os

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    USE_PASSLIB = True
    print("✅ Database: Using passlib/bcrypt for password hashing")
except ImportError:
    USE_PASSLIB = False
    print("ℹ️ Database: Using hashlib.sha256 for password hashing")

# SQLite Configuration
DATABASE_URL = "sqlite:///./finbot_users.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ NEW SQLAlchemy 2.0 SYNTAX
Base = declarative_base()

# User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ========== COMPATIBLE HASH FUNCTIONS ==========

def get_password_hash(password: str) -> str:
    """Hash password - Streamlit compatible"""
    if USE_PASSLIB:
        return pwd_context.hash(password)
    else:
        return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password - Streamlit compatible"""
    if USE_PASSLIB:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            # Fallback to SHA256 if bcrypt fails
            return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
    else:
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def migrate_old_passwords():
    """Migrate old SHA256 passwords to bcrypt if necessary"""
    if not USE_PASSLIB:
        return  # No migration needed
    
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        migrated_count = 0
        
        for user in users:
            # Check if it's a SHA256 hash (64 hexadecimal characters)
            if len(user.password_hash) == 64 and all(c in '0123456789abcdef' for c in user.password_hash.lower()):
                print(f"⚠️ Detected old SHA256 hash for {user.email}")
                # We can't automatically migrate since we don't have the plain password
                # User will need to log in once more
                
        if migrated_count > 0:
            db.commit()
            print(f"✅ {migrated_count} passwords migrated to bcrypt")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

# ========== UTILITY FUNCTIONS ==========

def create_tables():
    """Create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========== USER MANAGEMENT ==========

def add_test_users():
    """Add test users with proper hash system"""
    
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_count = db.query(User).count()
        
        if existing_count > 0:
            print(f"ℹ️ {existing_count} users already present in the database")
            
            # Optional: migrate old passwords
            if USE_PASSLIB:
                migrate_old_passwords()
            
            db.close()
            return
        
        # Base test users
        test_users = [
            {"name": "Admin User", "email": "admin@finbot.com", "password": "admin123"},
            {"name": "Test User", "email": "test@finbot.com", "password": "test123"},
            {"name": "Demo User", "email": "demo@finbot.com", "password": "demo123"},
        ]
        
        print("🚀 Adding test users...")
        hash_method = "bcrypt" if USE_PASSLIB else "SHA256"
        print(f"🔐 Hash method used: {hash_method}")
        
        for user_data in test_users:
            hashed_password = get_password_hash(user_data["password"])
            
            db_user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=hashed_password
            )
            
            db.add(db_user)
            print(f"➕ {user_data['name']} ({user_data['email']}) - password: {user_data['password']}")
        
        db.commit()
        print("✅ All test users have been added!")
        
    except Exception as e:
        print(f"❌ Error adding users: {e}")
        db.rollback()
    finally:
        db.close()

def authenticate_user(email: str, password: str):
    """Authenticate a user - compatible with all hash systems"""
    
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.email == email.strip().lower()).first()
        
        if not user:
            return {"success": False, "message": "Email not found"}
        
        # Try verification with current system
        password_valid = verify_password(password, user.password_hash)
        
        if not password_valid:
            return {"success": False, "message": "Incorrect password"}
        
        # If using passlib and user has old SHA256 hash,
        # we can update it now that we have the plain password
        if USE_PASSLIB and len(user.password_hash) == 64:
            try:
                new_hash = pwd_context.hash(password)
                user.password_hash = new_hash
                db.commit()
                print(f"🔄 Password migrated to bcrypt for {email}")
            except Exception as e:
                print(f"⚠️ Migration failed for {email}: {e}")
        
        return {
            "success": True,
            "user_name": user.name,
            "user_email": user.email,
            "message": "Login successful"
        }
        
    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}
    finally:
        db.close()

def add_single_user(name: str, email: str, password: str):
    """Add a single user"""
    
    db = SessionLocal()
    
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == email.lower()).first()
        
        if existing_user:
            print(f"❌ Email {email} already exists!")
            return False
        
        # Create user with proper hash
        hashed_password = get_password_hash(password)
        
        new_user = User(
            name=name,
            email=email.lower(),
            password_hash=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        
        hash_method = "bcrypt" if USE_PASSLIB else "SHA256"
        print(f"✅ User added: {name} ({email}) - Hash: {hash_method}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_login(email: str, password: str):
    """Test a login"""
    
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.email == email.lower()).first()
        
        print(f"\n🔐 Login test for: {email}")
        print("-" * 40)
        
        if not user:
            print("❌ Email not found")
            return False
        
        # Display debug info
        hash_length = len(user.password_hash)
        hash_type = "bcrypt" if hash_length > 64 else "SHA256"
        print(f"🔍 Stored hash: {hash_type} ({hash_length} characters)")
        
        if verify_password(password, user.password_hash):
            print(f"✅ Login successful for {user.name}!")
            return True
        else:
            print("❌ Incorrect password")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()

def list_all_users():
    """Display all users with hash info"""
    
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        
        if not users:
            print("📭 No users in the database")
            return
        
        print("\n" + "="*70)
        print("👥 LIST OF ALL USERS")
        print("="*70)
        
        for i, user in enumerate(users, 1):
            hash_length = len(user.password_hash)
            hash_type = "bcrypt" if hash_length > 64 else "SHA256"
            
            print(f"""
{i}. 👤 {user.name}
   📧 Email: {user.email}
   🆔 ID: {user.id}
   🔐 Hash: {hash_type} ({hash_length} chars)
   📅 Created: {user.created_at.strftime('%d/%m/%Y at %H:%M')}
   {"-"*60}""")
        
        print(f"\n📊 Total: {len(users)} users")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

def initialize_database():
    """Completely initialize the database"""
    
    print("🚀 DATABASE INITIALIZATION")
    print("="*50)
    
    # Display hash method used
    hash_method = "passlib/bcrypt" if USE_PASSLIB else "hashlib/SHA256"
    print(f"🔐 Hash method: {hash_method}")
    
    # 1. Create tables
    print("\n1️⃣ Creating tables...")
    if not create_tables():
        return False
    
    # 2. Add test users
    print("\n2️⃣ Adding test users...")
    add_test_users()
    
    # 3. Verify content
    print("\n3️⃣ Verifying content...")
    list_all_users()
    
    # 4. Test login
    print("\n4️⃣ Testing login...")
    test_login("admin@finbot.com", "admin123")
    
    print("\n" + "="*50)
    print("🎉 INITIALIZATION COMPLETE!")
    print("="*50)
    
    return True

# ========== ADDITIONAL USER MANAGEMENT FUNCTIONS ==========

def delete_user_by_email(email: str):
    """Delete a user by email"""
    
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.email == email.lower()).first()
        
        if not user:
            print(f"❌ User with email {email} not found")
            return False
        
        db.delete(user)
        db.commit()
        print(f"✅ User {user.name} ({email}) deleted successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def update_user_password(email: str, new_password: str):
    """Update a user's password"""
    
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.email == email.lower()).first()
        
        if not user:
            print(f"❌ User with email {email} not found")
            return False
        
        # Hash new password
        new_hash = get_password_hash(new_password)
        user.password_hash = new_hash
        db.commit()
        
        hash_method = "bcrypt" if USE_PASSLIB else "SHA256"
        print(f"✅ Password updated for {user.name} ({email}) - Hash: {hash_method}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def get_user_stats():
    """Get database statistics"""
    
    db = SessionLocal()
    
    try:
        total_users = db.query(User).count()
        
        if total_users == 0:
            return {"total_users": 0, "latest_user": None, "hash_distribution": {}}
        
        # Get latest user
        latest_user = db.query(User).order_by(User.created_at.desc()).first()
        
        # Check hash distribution
        users = db.query(User).all()
        bcrypt_count = 0
        sha256_count = 0
        
        for user in users:
            if len(user.password_hash) > 64:
                bcrypt_count += 1
            else:
                sha256_count += 1
        
        return {
            "total_users": total_users,
            "latest_user": {
                "name": latest_user.name,
                "email": latest_user.email,
                "created_at": latest_user.created_at.strftime('%d/%m/%Y at %H:%M')
            },
            "hash_distribution": {
                "bcrypt": bcrypt_count,
                "sha256": sha256_count
            }
        }
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return {"error": str(e)}
    finally:
        db.close()

def verify_database_integrity():
    """Verify database integrity"""
    
    print("🔍 VERIFYING DATABASE INTEGRITY")
    print("-" * 40)
    
    try:
        # Test connection
        db = SessionLocal()
        db.execute("SELECT 1").fetchone()
        print("✅ Database connection: OK")
        
        # Check table existence
        result = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
        if result:
            print("✅ Users table: EXISTS")
        else:
            print("❌ Users table: MISSING")
            return False
        
        # Check data integrity
        users = db.query(User).all()
        print(f"✅ Total users: {len(users)}")
        
        # Check for required fields
        invalid_users = 0
        for user in users:
            if not user.name or not user.email or not user.password_hash:
                invalid_users += 1
        
        if invalid_users == 0:
            print("✅ Data integrity: ALL USERS VALID")
        else:
            print(f"⚠️ Data integrity: {invalid_users} invalid users found")
        
        # Check hash formats
        bcrypt_users = sum(1 for user in users if len(user.password_hash) > 64)
        sha256_users = sum(1 for user in users if len(user.password_hash) == 64)
        
        print(f"🔐 Hash distribution: {bcrypt_users} bcrypt, {sha256_users} SHA256")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database integrity check failed: {e}")
        return False
