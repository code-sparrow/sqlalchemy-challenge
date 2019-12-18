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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Calculate the date 1 year ago from the last data point in the database
session = Session(engine)
latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
parsed_date = (latest).split('-')
minus_year = int(parsed_date[0]) - 1
year_earlier = f'{minus_year}-{parsed_date[1]}-{parsed_date[2]}'
session.close()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as the key and prcp as the value.
        Return the JSON representation of your dictionary."""

    #doesn't really specify what query to convert
    #queried last year of data for dates and prcp
    
    session = Session(engine)
    prcp_query = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_earlier).all()
    session.close()

    prcp_dict = dict(prcp_query)

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""

    session = Session(engine)
    station_query = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(station_query))

    # Jsonify summary
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point.
    Return a JSON list of Temperature Observations (tobs) for the previous year."""

    session = Session(engine)
    tobs_query = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_earlier).all()
    session.close()

    tobs_list = list(np.ravel(tobs_query))

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def t_start(start):
    """Return a JSON list of the minimum temperature, the average temperature, 
    and the max temperature for a given start date.
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater
    than and equal to the start date."""

    session = Session(engine)
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    t_start_query = session.query(*sel).filter(Measurement.date >= start).all()
    session.close()
    t_start_list = list(np.ravel(t_start_query))
    return jsonify(t_start_list)

@app.route("/api/v1.0/<start>/<end>")
def t_start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature,
    and the max temperature for a given start-end date range.
    When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
    for dates between the start and end date inclusive."""

    session = Session(engine)
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    t_start_end_query = session.query(*sel).filter(Measurement.date.between(start, end)).all()
    session.close()
    t_start_end_list = list(np.ravel(t_start_end_query))
    return jsonify(t_start_end_list)

if __name__ == '__main__':
    app.run(debug=True)