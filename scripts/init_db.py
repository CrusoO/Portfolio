#!/usr/bin/env python3
"""
Database initialization script
Creates tables and optionally adds sample data
"""
import sys
import os

# Add the parent directory to the path so we can import our app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, SessionLocal
from app.core.security import get_password_hash
from app.models import Base, User, Note
import json


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")


def create_admin_user():
    """Create default admin user"""
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("⚠️  Admin user already exists")
            return
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@portfolio.com",
            first_name="Robinson",
            last_name="Admin",
            hashed_password=get_password_hash("admin123"),
            is_admin=True,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   ⚠️  Please change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


def create_sample_notes():
    """Create sample blog notes"""
    db = SessionLocal()
    try:
        # Check if notes already exist
        existing_notes = db.query(Note).count()
        if existing_notes > 0:
            print("⚠️  Sample notes already exist")
            return
        
        sample_notes = [
            {
                "title": "Square Peg, Round World",
                "content": """
In a world that often celebrates conformity, being different can feel like being a square peg trying to fit into a round hole. But perhaps the problem isn't with the peg—perhaps it's with our understanding of what holes can accommodate.

I've learned that our differences aren't obstacles to overcome; they're features to embrace. When we stop trying to sand off our edges to fit into spaces that weren't meant for us, we discover that we can create our own spaces—spaces where our unique shape isn't just accepted, but valued.

The technology industry, despite its reputation for innovation, can sometimes feel surprisingly uniform. But the most groundbreaking solutions often come from those who think differently, who approach problems from unexpected angles, who refuse to accept that things must be done the way they've always been done.

Being different isn't a bug—it's a feature. And the world needs more square pegs willing to show that round holes aren't the only option.
                """.strip(),
                "snippet": "On being different in a world of conformity and why our unique perspectives are actually our greatest strengths.",
                "category": "Identity",
                "tags": ["Being Different", "Society", "Technology", "Innovation"],
                "read_time": 6,
                "is_published": "published"
            },
            {
                "title": "The Man Who Collected Shadows",
                "content": """
I met him at Bangalore Railway Station during one of those monsoon evenings when the rain transforms the city into a watercolor painting. He was sitting on a bench, sketching something in a worn notebook, completely oblivious to the chaos around him.

"What are you drawing?" I asked, curiosity getting the better of me.

He looked up with eyes that seemed to hold stories I'd never heard. "Shadows," he said simply. "I collect them."

He showed me his notebook—page after page of shadows. Not the objects that cast them, just the shadows. The shadow of a woman waiting for her train, the shadow of a child running to his mother, the shadow of an old man feeding pigeons.

"Why shadows?" I pressed.

He smiled. "Because shadows tell the truth. They show us who we are when we think nobody's looking. They capture moments we forget to notice. People pose for photographs, but shadows... shadows just are."

I think about him sometimes, especially when I'm debugging code late at night and my own shadow keeps me company on the wall. He taught me that there's beauty in the overlooked, truth in the forgotten, and stories in the spaces between the light.

Sometimes the most profound lessons come from the most unexpected teachers.
                """.strip(),
                "snippet": "A story from Bangalore Railway Station about finding beauty in the overlooked and wisdom in unexpected places.",
                "category": "Story",
                "tags": ["Story", "Bangalore", "Life Lessons", "Travel"],
                "read_time": 7,
                "is_published": "published"
            },
            {
                "title": "Code, Coffee, and Late Night Revelations",
                "content": """
There's something magical about coding in the quiet hours when the world is asleep. The hum of the computer, the glow of the screen, the endless possibility contained in empty files waiting to be filled with logic and dreams.

Tonight I'm working on a particularly stubborn algorithm. The kind that makes you question everything you know about programming, life, and whether you remembered to eat dinner. But these are the moments I live for—when the complexity of the problem matches the complexity of the solution you're building in your mind.

Coffee helps, of course. Not just for the caffeine, but for the ritual. The pause between attempts, the moment to think, the warmth that keeps your hands steady on the keyboard. I've solved more problems while waiting for my coffee to brew than I have during actual coding sessions.

There's a Zen to debugging that I think non-programmers might not understand. It's detective work, archaeology, and meditation all rolled into one. You trace the flow of data like a river, follow the breadcrumbs of logic, and sometimes—if you're very lucky or very persistent—you find the one missing semicolon that's been mocking you for the last three hours.

The satisfaction when it finally works is indescribable. Not just because the code runs, but because you've created something from nothing, brought order to chaos, made the impossible possible with nothing but your thoughts and twenty-six letters on a keyboard.

This is why I code. Not for the money or the prestige, but for these moments when the universe makes sense and you're the one who made it so.
                """.strip(),
                "snippet": "Reflections on the zen of programming, late-night coding sessions, and the satisfaction of solving complex problems.",
                "category": "Technology",
                "tags": ["Programming", "Coffee", "Life", "Problem Solving"],
                "read_time": 8,
                "is_published": "published"
            }
        ]
        
        for note_data in sample_notes:
            note = Note(**note_data)
            db.add(note)
        
        db.commit()
        print(f"✅ Created {len(sample_notes)} sample notes")
        
    except Exception as e:
        print(f"❌ Error creating sample notes: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main initialization function"""
    print("🚀 Initializing Robinson's Portfolio Backend Database")
    print("=" * 50)
    
    try:
        create_tables()
        create_admin_user()
        create_sample_notes()
        
        print("\n🎉 Database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Start the server: python run.py")
        print("2. Visit http://localhost:8000/docs for API documentation")
        print("3. Change the default admin password")
        
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
