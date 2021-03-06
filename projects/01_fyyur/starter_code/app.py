#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)



# TODO: [Done] connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.String)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(400))
    show = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
        return f'<Venue{self.id} {self.name}>'
        # return {
        # 'id' : self.id,
        # 'name' : self.name,
        # 'genres' : self.genres,
        # 'city' : self.city,
        # 'state' : self.state,
        # 'phone' : self.phone,
        # 'image_link' : self.image_link,
        # 'website' : self.website,
        # 'facebook_link' : self.facebook_link,
        # 'seeking_talent' : self.seeking_talent,
        # 'seeking_description' : self.seeking_description,
        # 'past_shows': [],
        # 'upcoming_shows': [],
        # 'past_shows_count': 0,
        # 'upcoming_shows_count': 0
        #
        # }



    # TODO: [Done] implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(400))
    show = db.relationship('Show', backref='Artist', lazy=True)


def __repr__(self):
    return f'<Artist{self.id} {self.name}>'

    # TODO: [Done] implement any missing fields, as a database migration using Flask-Migrate Done


class Show(db.Model):
    __tablename = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

def __repr__(self):
    return f'<Show{self.id} , Artist{self.artist_id} , Venue{self.venue_id}>'

# TODO [Done] Implement Show and Artist models, and complete all model relationships and properties, as a database migration.Done



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
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: [Done]replace with real venues data.
  #      num_shows should be aggregated based on number of upcoming shows per venue.

  data = []


  venues = Venue.query.all()

  #venues = session.query(Venue).all
  #venues_location = Venue.query.with_entities(Venue.city, Venue.state)
  venues_location = Venue.query.with_entities(Venue.state, Venue.city).group_by(Venue.state, Venue.city).order_by(Venue.state).all()

  for location in venues_location:
      data.append({
      "city": location[0],
      "state": location[1],
      "venues": []
      })

  for venue in venues:
      upcoming_shows = 0

      shows = Show.query.filter_by(venue_id=venue.id).all



      for show in shows:
          if show.start_time > datetime.now():
             upcoming_shows += 1

      for venue_location_list in data:
         if venue.state == venue_location_list['state'] and venue.city == venue_location_list['city']:
             venue_location_list['venues'].append({
             "id": venue.id,
             "name": venue.name,
             "num_upcoming_shows": upcoming_shows
             })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: [Done]implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_form = request.form.get('search_term', '')
  search_result = Venue.query.filter(Venue.name.ilike(f'%{search_form}%')).all()
  #somecolumn.ilike("foo/%bar", escape="/")

  #len (venues)
  response={
  "count":search_result.count(),
  "data": search_result
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO:[Done] replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)

  #data=Todo.query.filter_by(list_id=list_id).order_by('id').all())

  shows = Show.query.filter_by(venue_id=venue_id).order_by('id').all()

  past_shows = []
  upcoming_shows = []


  for show in shows:
      shows_info = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
      }
      if show.start_time > datetime.now():
          upcoming_shows.append(show_info)
      else:
          past_shows.append(show_info)


  data={
    "id": venue.id,
    "name": venue.name,
    "genres":venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
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
     # TODO: [Done] insert form data as a new Venue record in the db, instead
     # TODO: [Done] modify data to be the data object returned from db insertion
    form = VenueForm()
    try:
        form = VenueForm()
        new_venue = Venue(
        name=form.name.data,
        genres=form.genres.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        website=form.website.data,
        facebook_link=form.facebook_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
        )
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except:
        db.session.rollback()
        # TODO: [Done] on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue '+ request.form['name'] + ' could not be listed')
        #print(sys.exc_info())
    finally:
        db.session.close()
        return render_template('pages/home.html')


  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: [Done] Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      venue_name = venue.name
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
      flash(venue_name + 'Venue was successfully deleted')

  except:
      db.session.rollback()
      flask('An error occurred. ' + venue_name + 'could not be deleted')
  finally:
      db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO:[Done]replace with real data returned from querying the database
  data = []

  artist_names = Artist.query.with_entities(Artist.id, Artist.name)


  for artist in artist_names:
      data.append({
      "id": artist.id,
      "name": artist.name,

      })


  """data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]"""

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO:[Done] implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_form = request.form.get('search_term', '')
  search_result = Artist.query.filter(Artist.name.ilike(f'%{search_form}%'))


  response={
    "count": search_result.count(),
    "data": search_result
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO:[Done] replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(venue_id=venue_id).order_by('id').all()

  past_shows = []
  upcoming_shows = []

  for show in shows:
      shows_info = {
      "venue_id": show.venue_id,
      "venue_name": show.venue_name,
      "venue_image_link": show.venue.image_link,
      "start_time": format_datetime(str(show.start_time))
      }
      if show.start_time > datetime.now():
          upcoming_shows.append(show_info)
      else:
          past_shows.append(show_info)



  data={
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "genres": artist.genres,
    "image_link": artist.image_link,
    "facebook_link": artist.facebook_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),

  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  # TODO: [Done] populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  data={
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "genres": artist.genres,
    "image_link": artist.image_link,
    "facebook_link": artist.facebook_link,
    }

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  try:
      artist = Artist.query.filter_by(artist_id=artist_id).one()
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.date
      artist.phone = form.phone.data
      artist.website = form.website.data
      artist.genres = form.genres.data
      artist.image_link = form.image_link.data
      artist.facebook_link = form.facebook_link.data

      db.session.commit()
      flash('Artist'+ request.form['name'] + ' was successfully updated')
  except:
      db.session.rollback()
      flash('Artist'+ request.form['name'] + 'could not be updated')
  finally:
      db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  # TODO: [Done] populate form with values from venue with ID <venue_id>

  data={
     "id": venue.id,
     "name": venue.name,
     "genres": venue.genres,
     "city": venue.city,
     "state": venue.state,
     "address": venue.address,
     "phone": venue.phone,
     "image_link": venue.image_link,
     "website": venue.website,
     "facebook_link": venue.facebook_link,

   }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    try:
        venue = Venue.query.filter_by(venue_id=venue_id).one()
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.image_link = form.image_link.data
        venue.website = form.website.data
        venue.facebook_link = form.facebook_link.data

        db.session.commit()
        flash('Venue'+ request.form['name'] + ' was successfully updated')
    except:
        db.session.rollback()
        flash('Venue'+ request.form['name'] + 'could not be updated')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


  # TODO: [Done] take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: [Done] insert form data as a new Venue record in the db, instead
    # TODO:[Done] modify data to be the data object returned from db insertion
    try:
        form = ArtistForm()
        new_artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        website = form.website.data,
        genres = form.genres.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        )
        db.session.add(new_artist)
        db.session.commit()

        # [Done] on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except:
        db.session.rollback()
        # TODO: [Done] on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        flash('An error occurred. Artist '+ request.form['name'] + ' could not be listed')
        #print(sys.exc_info())
    finally:
        db.session.close()
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: [Done] replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data = []

  shows = Show.query.all()

  for show in shows:
      data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue_name,
      "artist_id": show.artist_id,
      "artist_image_link": show.artist_image_link,
      "start_time": show.artist_time
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
    # TODO: [Done] insert form data as a new Show record in the db, instead
    try:
        form = ShowForm()
        new_show = Shows(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time = form.start_time.data
        )
        db.session.add(new_show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
        db.session.rollback()
        flash('Show was not successfully listed!')
    finally:
        db.session.close()


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
