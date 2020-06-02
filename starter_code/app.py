#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import date, datetime
from sqlalchemy.sql.expression import label
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(300))
    genres = db.Column(db.ARRAY(db.String()))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(300))
    added = db.Column(db.DateTime, default=datetime.utcnow)
    shows = db.relationship('Show', backref='venue', lazy=True, cascade='all, delete-orphan', 
      passive_deletes=True)
    
    def __repr__(self):
      return '<Venue {}>'.format(self.name)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    added = db.Column(db.DateTime, default=datetime.utcnow)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(300))
    shows = db.relationship('Show', backref='artist', passive_deletes=True, lazy=True)
    def __repr__(self):
      return '<Artist {}>'.format(self.name)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key = True)
    start_time = db.Column(db.DateTime)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete= 'CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False)
    def __repr__(self):
      return '<Show {}>'.format(self.artist_id, self.venue_id)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  artist = db.session.query(Artist.id, Artist.name, label('added', Artist.added))
  venue = db.session.query(Venue.id, Venue.name, label('added', Venue.added))
  join_added = venue.union_all(artist).order_by('added')
  return render_template('pages/home.html', join_added=join_added)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  location = Venue.query.distinct(Venue.state, Venue.city).all()
  data = []
  now = datetime.utcnow()
  for venue in location:
    venue = {
      'city': venue.city,
      'state': venue.state,
    }
    venue['venues'] = []
    venue_iter = Venue.query.filter_by(city=venue['city'], state=venue['state']).all()
    for venue_data in venue_iter:
      numberOfUpcomingShows = db.session.query(Venue).join(Show, Show.venue_id == Venue.id).filter(Show.start_time>now).count()
      venues_dict= {
        'id': venue_data.id,
        'name': venue_data.name,
        'num_upcoming_shows': numberOfUpcomingShows,
      }
      venue['venues'].append(venues_dict)
    data.append(venue.copy())
  return render_template('pages/venues.html', areas=data)

 
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  response={
    "count": len(venues)
  }
  response['data']=[]
  for venue in venues:
    response['data'].append({
      "id": venue.id,
      "name": venue.name,
    })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue_data_all = Venue.query.filter_by(id=venue_id).all()
  data = []
  now = datetime.utcnow()
  for venue_data in venue_data_all:
    venues_dict={
      'id': venue_data.id,
      'name': venue_data.name,
      'genres': venue_data.genres,
      'address': venue_data.address,
      'city': venue_data.city,
      'state': venue_data.state,
      'phone': venue_data.phone,
      'website': venue_data.website_link,
      'facebook_link': venue_data.facebook_link,
      'seeking_talent': venue_data.seeking_talent,
      'seeking_description': venue_data.seeking_description,
      'image_link': venue_data.image_link,
      'past_shows_count': Show.query.filter(Show.venue_id == venue_id,Show.start_time < datetime.now()).count(),
      'upcoming_shows_count': Show.query.filter(Show.venue_id == venue_id,Show.start_time > datetime.now()).count()
    }
    venues_dict['past_shows'] = []
    venues_dict['upcoming_shows']=[]
    past_shows_query = db.session.query(Artist.id, Artist.name, Artist.image_link, Show.start_time).join(Show, Artist.id == Show.artist_id).filter(Show.venue_id == venue_id, Show.start_time < now).all()
    for past_show in past_shows_query:
      venues_dict['past_shows'].append({
        'artist_id': past_show.id,
        'artist_name': past_show.name,
        'artist_image_link': past_show.image_link,
        'start_time': past_show.start_time.strftime("%m/%d/%Y, %H:%M")
      })
    upcoming_shows_query = db.session.query(Artist.id, Artist.name, Artist.image_link, Show.start_time).join(Show, Artist.id == Show.artist_id).filter(Show.venue_id == venue_id, Show.start_time > now).all()
    for upcoming_show in upcoming_shows_query:
      venues_dict['upcoming_shows'].append({
        'artist_id': upcoming_show.id,
        'artist_name': upcoming_show.name,
        'artist_image_link': upcoming_show.image_link,
        'start_time': upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M")
      })
  data.append(venues_dict)
  data = list(filter(lambda d: d['id'] == venue_id, data))[0]
  return render_template('pages/show_venue.html', venue=data)
  
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  data = request.form
  vname = data['name']
  vcity = data['city']
  vstate = data['state']
  vaddress = data['address']
  vphone = data['phone']
  vgenres = request.form.getlist('genres')
  vfb_link = data['facebook_link']
  vimage_link = data['image_link']
  vwebsite = data['website_link']
  vseek = request.form.get('seeking_talent')
  if vseek == 'y':
    vseeking_talent= True
  else:
    vseeking_talent = vseek
  vseeking_description = request.form.get('seeking_description')
  try:
    db.session.add(Venue(
      city=vcity,
      state=vstate,
      name=vname,
      address=vaddress,
      phone=vphone,
      facebook_link=vfb_link,
      website_link=vwebsite,
      genres=vgenres,
      image_link=vimage_link,
      seeking_talent=vseeking_talent,
      seeking_description=vseeking_description
    ))
  except expression:
    print(e)
    error = true
  finally:
    if not error:
      db.session.commit()
      flash('Venue ' + request.form['name'] +
        ' was successfully listed!')
      artist = db.session.query(Artist.id, Artist.name, label('added', Artist.added))
      venue = db.session.query(Venue.id, Venue.name, label('added', Venue.added))
      join_added = venue.union_all(artist).order_by('added')
    else:
      flash('An error occurred. Venue ' +
        vname + ' could not be listed.')
      db.session.rollback()
  return render_template('pages/home.html', join_added=join_added)
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/venues.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist_full = Artist.query.all()
  data = []
  for artist_data in artist_full:
    artist_dict={
      'id': artist_data.id,
      'name': artist_data.name
    }
    data.append(artist_dict)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  response={
    "count": len(artists)
  }
  response['data']=[]
  for artist in artists:
    response['data'].append({
      "id": artist.id,
      "name": artist.name,
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist_data_all = Artist.query.filter_by(id=artist_id).all()
  data = []
  now = datetime.utcnow()
  for artist_data in artist_data_all:
    artist_dict={
      'id': artist_data.id,
      'name': artist_data.name,
      'genres': artist_data.genres,
      'city': artist_data.city,
      'state': artist_data.state,
      'phone': artist_data.phone,
      'website': artist_data.website_link,
      'facebook_link': artist_data.facebook_link,
      'seeking_venue': artist_data.seeking_venue,
      'seeking_description': artist_data.seeking_description,
      'image_link': artist_data.image_link,
      'past_shows_count': Show.query.filter(Show.artist_id == artist_id, Show.start_time < datetime.now()).count(),
      'upcoming_shows_count': Show.query.filter(Show.artist_id == artist_id, Show.start_time > datetime.now()).count()
    }
    artist_dict['past_shows'] = []
    artist_dict['upcoming_shows']=[]
    past_shows_query = db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time).join(Show, Venue.id == Show.venue_id).filter(Show.artist_id == artist_id, Show.start_time < now).all()
    for past_show in past_shows_query:
      artist_dict['past_shows'].append({
        'venue_id': past_show.id,
        'venue_name': past_show.name,
        'venue_image_link': past_show.image_link,
        'start_time': past_show.start_time.strftime("%m/%d/%Y, %H:%M")
      })
    upcoming_shows_query = db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time).join(Show, Venue.id == Show.venue_id).filter(Show.artist_id == artist_id, Show.start_time > now).all()
    for upcoming_show in upcoming_shows_query:
      artist_dict['upcoming_shows'].append({
        'venue_id': upcoming_show.id,
        'venue_name': upcoming_show.name,
        'venue_image_link': upcoming_show.image_link,
        'start_time': upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M")
      })
  data.append(artist_dict)
  data = list(filter(lambda d: d['id'] == artist_id, data))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    aseek = request.form.get('seeking_venue')
    if aseek == 'y':
      artist.seeking_venue = True
    else:
      artist.seeking_venue = aseek
    artist.seeking_description = request.form.get('seeking_description')
    db.session.commit()
    flash('Artist was edited to be ' + request.form['name'] + ' successfully!')
  except:
    error = True
    flash('Artist was not edited successfully!')
    print(sys.exc_info)
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    vseek = request.form.get('seeking_talent')
    if vseek == 'y':
      venue.seeking_talent = True
    else:
      venue.seeking_talent = vseek
    venue.seeking_description = request.form.get('seeking_description')
    db.session.commit()
    flash('Venue was edited to be ' + request.form['name'] + ' successfully!')
  except:
    print(e)
    flash('Venue was not edited successfully!')
    db.session.rollback()
  finally:
    db.session.close()
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  data = request.form
  vname = data['name']
  vcity = data['city']
  vstate = data['state']
  vphone = data['phone']
  vgenres = request.form.getlist('genres')
  vfb_link = data['facebook_link']
  vimage_link = data['image_link']
  vwebsite = data['website_link']
  vseek = request.form.get('seeking_venue')
  if vseek == 'y':
    vseeking_venue= True
  else:
    vseeking_venue = vseek
  vseeking_description = request.form.get('seeking_description')
  try:
    db.session.add(Artist(
      city=vcity,
      state=vstate,
      name=vname,
      phone=vphone,
      facebook_link=vfb_link,
      website_link=vwebsite,
      genres=vgenres,
      image_link=vimage_link,
      seeking_venue=vseeking_venue,
      seeking_description=vseeking_description
    ))
  except expression:
    error = true
    print(sys.exc_info)
  finally:
    if not error:
      db.session.commit()
      flash('Artist ' + request.form['name'] +
        ' was successfully listed!')
      artist = db.session.query(Artist.id, Artist.name, label('added', Artist.added))
      venue = db.session.query(Venue.id, Venue.name, label('added', Venue.added))
      join_added = artist.union_all(venue).order_by('added')
    else:
      flash('An error occurred. Artist ' +
        vname + ' could not be listed.')
      db.session.rollback()
  return render_template('pages/home.html', join_added=join_added)
  
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/artists.html')
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = db.session.query(Show.artist_id, Show.venue_id, Show.start_time).all()
  for show in shows:
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show[0]).one()
    venue = db.session.query(Venue.name).filter(Venue.id == show[1]).one()
    data.append({
      "venue_id": show[1],
      "venue_name": venue[0],
      "artist_id": show[0],
      "artist_name": artist[0],
      "artist_image_link": artist[1],
      "start_time": str(show[2])
    })
  return render_template('pages/shows.html', shows=data)  

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  date_format = '%Y-%m-%d %H:%M:%S'
  try:
    new_show = Show(
      artist_id = request.form['artist_id'],
      venue_id = request.form['venue_id'],
      start_time = datetime.strptime(request.form['start_time'], date_format)
    )
    db.session.add(new_show)
    db.session.commit()
  except:
    error = True
    flash('An error occurred! Show could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
    if error: 
      flash('An error occurred! Show could not be listed.')
    else:
      flash('Show is successfully listed!')
      artist = db.session.query(Artist.id, Artist.name, label('added', Artist.added))
      venue = db.session.query(Venue.id, Venue.name, label('added', Venue.added))
      join_added = venue.union_all(artist).order_by('added')
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
