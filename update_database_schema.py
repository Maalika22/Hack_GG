"""
Update database schema to add new columns
Run this once to add new fields to existing database
"""

from app import app
from models import db
from sqlalchemy import text

def update_schema():
    """Add new columns to existing tables"""
    with app.app_context():
        try:
            # Check if columns exist and add them if they don't
            with db.engine.connect() as conn:
                # Check and add is_third_party column
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='user' AND column_name='is_third_party'
                """))
                if not result.fetchone():
                    conn.execute(text("ALTER TABLE \"user\" ADD COLUMN is_third_party BOOLEAN DEFAULT FALSE"))
                    conn.commit()
                    print("[OK] Added is_third_party column")
                
                # Check and add email_verified column
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='user' AND column_name='email_verified'
                """))
                if not result.fetchone():
                    conn.execute(text("ALTER TABLE \"user\" ADD COLUMN email_verified BOOLEAN DEFAULT FALSE"))
                    conn.commit()
                    print("[OK] Added email_verified column")
                
                # Check if OTP table exists
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name='otp'
                """))
                if not result.fetchone():
                    print("[OK] Creating OTP table...")
                    db.create_all()
                
                # Check and add allocation fields to maintenance_request
                allocation_fields = [
                    ('allocation_status', 'VARCHAR(20) DEFAULT \'pending\''),
                    ('allocated_to_id', 'INTEGER'),
                    ('allocated_at', 'TIMESTAMP'),
                    ('worker_response', 'VARCHAR(20)'),
                    ('worker_response_at', 'TIMESTAMP'),
                    ('worker_response_reason', 'TEXT'),
                    ('proposed_deadline', 'TIMESTAMP'),
                    ('deadline_status', 'VARCHAR(20)'),
                    ('deadline_admin_response', 'TEXT'),
                    ('admin_instructions', 'TEXT'),
                    ('deadline_approved_at', 'TIMESTAMP')
                ]
                
                for field_name, field_type in allocation_fields:
                    result = conn.execute(text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='maintenance_request' AND column_name='{field_name}'
                    """))
                    if not result.fetchone():
                        conn.execute(text(f"ALTER TABLE maintenance_request ADD COLUMN {field_name} {field_type}"))
                        conn.commit()
                        print(f"[OK] Added {field_name} column to maintenance_request")
                
                # Add foreign key constraint for allocated_to_id if it doesn't exist
                result = conn.execute(text("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name='maintenance_request' 
                    AND constraint_name='maintenance_request_allocated_to_id_fkey'
                """))
                if not result.fetchone():
                    try:
                        conn.execute(text("""
                            ALTER TABLE maintenance_request 
                            ADD CONSTRAINT maintenance_request_allocated_to_id_fkey 
                            FOREIGN KEY (allocated_to_id) REFERENCES "user"(id)
                        """))
                        conn.commit()
                        print("[OK] Added foreign key constraint for allocated_to_id")
                    except Exception as e:
                        print(f"[INFO] Foreign key constraint may already exist: {e}")
                
                print("\n[OK] Database schema updated successfully!")
        except Exception as e:
            print(f"[ERROR] Error updating schema: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    update_schema()

