##########
# Step 2 - Climate App
#
#   Now that you have completed your initial analysis, design a Flask api 
#   based on the queries that you have just developed.
#
#      * Use FLASK to create your routes.
#
#   Routes
#
#       * `/api/v1.0/precipitation`
#           * Query for the dates and precipitation observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#           * Return the json representation of your dictionary.
#
#       * `/api/v1.0/stations`
#           * Return a json list of stations from the dataset.
#
#       * `/api/v1.0/tobs`
#           * Return a json list of Temperature Observations (tobs) for the previous year
#
#       * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
#           * Return a json list of the minimum temperature, the average temperature, and
#               the max temperature for a given start or start-end range.
#           * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates 
#               greater than and equal to the start date.
#           * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` 
#               for dates between the start and end date inclusive.
##########
# import dependencies 
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)
# reflect the database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return  """ <html>
                <b>Available Routes:</b><br/>
                <br/>
                <a href=\"/api/v1.0/precipitation\"><i>/api/v1.0/precipitation</i></a> - List of prior year rain totals from all stations<br/>
                    <br/>
                <a href=\"/api/v1.0/stations\"><i>/api/v1.0/stations</i></a> - List of Station numbers and names<br/>
                    <br/>
                <a href=\"/api/v1.0/tobs\"><i>/api/v1.0/tobs</i></a> - List of prior year temperatures from all stations<br/>
                    <br/>
                <a href=\"/api/v1.0/2017-01-01\"><i>/api/v1.0/2017-01-01</i></a> - When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>
                    <br/>
                <a href=\"/api/v1.0/2017-01-01/2017-01-07\"><i>/api/v1.0/start/2017-01-01/2017-01-07</i></a><br/> - When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>
            </html> """



@app.route("/api/v1.0/precipitation")
def precipitation():
    # Docstring 
    """Return a list of precipitations from last year"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]

    # Calculate the date 1 year ago from today
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    results_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    # Convert list of tuples into normal list
    precipitation_dict = dict(results_precipitation)
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Docstring
    """Return a JSON list of stations from the dataset."""
    results_stations =  session.query(Measurement.station).group_by(Measurement.station).all()
    stations_list = list(np.ravel(results_stations))
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Docstring
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""

    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]

    # Calculate the date 1 year ago from today
    # The days are equal 365 so that the first day of the year is included
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days = 365)
    # Query tobs
    results_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()
    tobs_list = list(results_tobs)
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def trip1(start):
    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""

    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    from_start_list = list(from_start)
    return jsonify(from_start_list)


@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):
    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list=list(between_dates)
    return jsonify(between_dates_list)


if __name__ == "__main__":
    app.run(debug=True)
