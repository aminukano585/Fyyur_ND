from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# shows = db.Table('shows',
#   db.Column('id', db.Integer, primary_key=True),
#   db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), nullable=False),
#   db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), nullable=False),
#   db.Column('start_time', db.DateTime, nullable=False, default=datetime.utcnow)
# )
class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  def __repr__(self):
    return f'<Show {self.id} {self.start_time}>'


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False, default=[])
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    shows = db.relationship('Show', backref=db.backref('venues', lazy=True), cascade='all, delete-orphan', lazy='subquery')

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'
    

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False, default=[])
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    shows = db.relationship('Show', backref=db.backref('artists', lazy=True), cascade='all, delete-orphan', lazy='subquery')

    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'
   

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

# DONE: Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
