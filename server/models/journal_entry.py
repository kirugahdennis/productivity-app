from sqlalchemy.orm import validates

from server.extensions import db

MOODS = ("happy", "sad", "anxious", "excited", "calm", "angry", "neutral", "grateful")


class JournalEntry(db.Model):
    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    mood = db.Column(db.String, nullable=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Ownership - every entry belongs to exactly one user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    user = db.relationship("User", back_populates="journal_entries")

    @validates("title")
    def validate_title(self, key, title):
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        if len(title) > 120:
            raise ValueError("Title must be 120 characters or fewer")
        return title.strip()

    @validates("content")
    def validate_content(self, key, content):
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        return content.strip()

    @validates("mood")
    def validate_mood(self, key, mood):
        if mood is None or mood == "":
            return None
        mood = mood.strip().lower()
        if mood not in MOODS:
            raise ValueError(f"Mood must be one of: {', '.join(MOODS)}")
        return mood

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "mood": self.mood,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<JournalEntry {self.id}: {self.title[:20]!r}>"