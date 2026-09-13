import random

from faker import Faker

from server.app import create_app
from server.extensions import db
from server.models.user import User
from server.models.journal_entry import JournalEntry, MOODS

fake = Faker()


def seed():
    app = create_app()
    with app.app_context():
        print("Clearing existing data...")
        JournalEntry.query.delete()
        User.query.delete()

        print("Seeding users...")
        users = []
        # A known demo account so the frontend team can log in without
        # generating their own test user.
        demo = User(username="demo_user")
        demo.password_hash = "password123"
        db.session.add(demo)
        users.append(demo)

        for _ in range(4):
            user = User(username=fake.unique.user_name())
            user.password_hash = "password123"
            db.session.add(user)
            users.append(user)

        db.session.commit()

        print("Seeding journal entries...")
        for user in users:
            for _ in range(random.randint(8, 15)):
                entry = JournalEntry(
                    title=fake.sentence(nb_words=5).rstrip("."),
                    content=fake.paragraph(nb_sentences=5),
                    mood=random.choice(MOODS),
                    user_id=user.id,
                )
                db.session.add(entry)

        db.session.commit()
        print(f"Seeded {len(users)} users (password: 'password123') and their journal entries.")
        print("Demo login -> username: demo_user, password: password123")


if __name__ == "__main__":
    seed()