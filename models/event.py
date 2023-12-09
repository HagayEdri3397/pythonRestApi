from database import db
from sqlalchemy import func

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    venue = db.Column(db.String(100))
    participants = db.Column(db.Integer)
    startDate = db.Column(db.DateTime, nullable=False)
    createDate = db.Column(db.DateTime, default=func.now())
    hasReminder = db.Column(db.Boolean, default=False)
    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'location': self.location,
            'venue': self.venue,
            'participants': self.participants,
            'startDate': self.startDate.strftime('%Y-%m-%d %H:%M:%S'),
            'createDate': self.createDate.strftime('%Y-%m-%d %H:%M:%S')
        }
