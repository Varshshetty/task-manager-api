from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Task(db.Model):
    """A single task in the tracker."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="todo")  # todo | in-progress | done
    priority = db.Column(db.String(10), nullable=False, default="medium")  # low | medium | high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert this row into a plain dictionary so Flask can turn it into JSON."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
        }
