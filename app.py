#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# DONE: connect to a local postgresql database

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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


def get_upcoming_shows(shows):
  filtered_shows = list(filter(lambda s: s.start_time > datetime.now(), shows))
  data = []

  for filtered_show in filtered_shows:
    data.append({
      'venue_id': filtered_show.venues.id,
      'venue_name': filtered_show.venues.name,
      'venue_image_link': filtered_show.venues.image_link,
      'artist_id': filtered_show.artists.id,
      'artist_name': filtered_show.artists.name,
      'artist_image_link': filtered_show.artists.image_link,
      'start_time': format_datetime(filtered_show.start_time)
    })

  return data


def get_past_shows(shows):
  filtered_shows = list(filter(lambda s: s.start_time < datetime.now(), shows))
  data = []

  for filtered_show in filtered_shows:
    data.append({
      'venue_id': filtered_show.venues.id,
      'venue_name': filtered_show.venues.name,
      'venue_image_link': filtered_show.venues.image_link,
      'artist_id': filtered_show.artists.id,
      'artist_name': filtered_show.artists.name,
      'artist_image_link': filtered_show.artists.image_link,
      'start_time': format_datetime(filtered_show.start_time)
    })

  return data

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  res = Venue.query.all()
  venues = [x.__dict__ for x in res]

  for venue in venues:
    if venue['state'] in [v['state'] for v in data]:
      add_venue = {
        'id': venue['id'],
        'name': venue['name'],
        'num_upcoming_shows': len(get_upcoming_shows(venue['shows']))
      }

      for idx, x in enumerate(data):
        if x['state'] == venue['state']:
          data[idx]['venues'].append(add_venue)
      
    else:
      add_state = {
        'city': venue['city'],
        'state': venue['state'],
        'venues': [{
          'id': venue['id'],
          'name': venue['name'],
          'num_upcoming_shows': len(get_upcoming_shows(venue['shows']))
        }]
      }
      data.append(add_state)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response = {}
  data = []
  search_term = request.form.get('search_term', '')

  res = Venue.query.filter(
    Venue.name.ilike(f'%{search_term}%') |
    Venue.city.ilike(f'%{search_term}%') |
    Venue.state.ilike(f'%{search_term}%')
  ).all()

  venues = [x.__dict__ for x in res]

  for venue in venues:
    data.append({
      'id': venue['id'],
      'name': venue['name'],
      'num_upcoming_shows': len(get_upcoming_shows(venue['shows'])) 
    })

  response['count'], response['data'] = len(data), data

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  
  data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': get_past_shows(venue.shows),
    'upcoming_shows': get_upcoming_shows(venue.shows),
    'past_shows_count': len(get_past_shows(venue.shows)),
    'upcoming_shows_count': len(get_upcoming_shows(venue.shows)),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)

  if form.validate_on_submit():
    try:
      venue = Venue(
        name=form.name.data,
        genres=form.genres.data,
        address=form.address.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        website=form.website_link.data,
        facebook_link=form.facebook_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data,
        image_link=form.image_link.data
      )

      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    finally:
      db.session.close()

  else:
    flash('Invalid submission!')
    print(form.errors)

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  data = []
  res = Artist.query.all()
  artists = [x.__dict__ for x in res]

  for artist in artists:
    add_artist = {
      'id': artist['id'],
      'name': artist['name']
    }
    data.append(add_artist)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {}
  data = []
  search_term = request.form.get('search_term', '')

  res = Artist.query.filter(
    Artist.name.ilike(f'%{search_term}%') |
    Artist.city.ilike(f'%{search_term}%') |
    Artist.state.ilike(f'%{search_term}%')
  ).all()

  artists = [x.__dict__ for x in res]

  for artist in artists:
    data.append({
      'id': artist['id'],
      'name': artist['name'],
      'num_upcoming_shows': len(get_upcoming_shows(artist['shows'])) 
    })

  response['count'], response['data'] = len(data), data

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # DONE: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)

  genres = ''.join([str(i) for i in artist.genres])[1:-1].split(',')
  
  data = {
    'id': artist.id,
    'name': artist.name,
    'genres': genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'past_shows': get_past_shows(artist.shows),
    'upcoming_shows': get_upcoming_shows(artist.shows),
    'past_shows_count': len(get_past_shows(artist.shows)),
    'upcoming_shows_count': len(get_upcoming_shows(artist.shows)),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist.genres = ''.join([str(i) for i in artist.genres])[1:-1].split(',')

  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)

  if form.validate_on_submit():
    try:
      artist = Artist.query.get(artist_id)

      artist.name = form.name.data
      artist.genres = form.genres.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.website = form.website_link.data
      artist.facebook_link = form.facebook_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      artist.image_link = form.image_link.data

      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully edited!')

    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')

    finally:
      db.session.close()

  else:
    flash('Invalid submission!')
    print(form.errors)

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)

  if form.validate_on_submit():
    try:
      venue = Venue.query.get(venue_id)

      venue.name = form.name.data
      venue.genres = form.genres.data
      venue.address = form.address.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.website = form.website_link.data
      venue.facebook_link = form.facebook_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      venue.image_link = form.image_link.data

      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully edited!')

    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')

    finally:
      db.session.close()

  else:
    flash('Invalid submission!')
    print(form.errors)

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)

  if form.validate_on_submit():
    try:
      artist = Artist(
        name=form.name.data,
        genres=form.genres.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        website=form.website_link.data,
        facebook_link=form.facebook_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data,
        image_link=form.image_link.data
      )

      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

    finally:
      db.session.close()

  else:
    flash('Invalid submission!')
    print(form.errors)

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  data = []
  shows = Show.query.all()
  
  for show in shows:
    data.append({
      'venue_id': show.venues.id,
      'venue_name': show.venues.name,
      'artist_id': show.artists.id,
      'artist_name': show.artists.name,
      'artist_image_link': show.artists.image_link,
      'start_time': format_datetime(show.start_time)
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)

  if form.validate_on_submit():
    try:
      show = Show(
        venue_id=form.venue_id.data,
        artist_id=form.artist_id.data,
        start_time=form.start_time.data,
      )

      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')

    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Show could not be listed.')

    finally:
      db.session.close()

  else:
    flash('Invalid submission!')
    print(form.errors)

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
