import sys
import os

# Add root folder to Python path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base, SessionLocal
from app.models.models import User, Document, JobRole

def init_database():
    print("Connecting to Neon Cloud Postgres...")
    
    # Create all 6 tables in Neon if they don't exist yet
    Base.metadata.create_all(bind=engine)
    print("All 6 tables created successfully in Neon Postgres!")

    # Test inserting a User and a Document
    db = SessionLocal()
    try:
        test_email = "sokha.meng@test.com"
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == test_email).first()
        if not existing_user:
            print("Creating a test user: Sokha Meng...")
            new_user = User(
                full_name="Sokha Meng",
                email=test_email
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user_id = new_user.id
            print(f"User saved! Assigned UUID: {user_id}")
        else:
            user_id = existing_user.id
            print(f"User already exists with UUID: {user_id}")

        # Insert a sample parsed document for this user
        new_doc = Document(
            user_id=user_id,
            doc_type="resume",
            file_name="sokha_resume.pdf",
            raw_text="Sample raw resume content...",
            parsed_skills=["Python", "FastAPI", "PostgreSQL", "Git"],
            parsed_coursework=["Data Structures", "Database Systems"],
            gpa=3.65,
            major="Computer Science"
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        print(f"Document record saved! Document UUID: {new_doc.id}")

        # Query the database to verify the insert worked
        saved_doc = db.query(Document).filter(Document.id == new_doc.id).first()
        print("\nVerification Query from Neon Cloud:")
        print(f"- File Name : {saved_doc.file_name}")
        print(f"- Major     : {saved_doc.major}")
        print(f"- GPA       : {saved_doc.gpa}")
        print(f"- Skills    : {saved_doc.parsed_skills}")
        print("\nPERSISTENCE COMPLETE! The data is now live on the cloud.")

    except Exception as e:
        db.rollback()
        print(f"Error during database test: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()