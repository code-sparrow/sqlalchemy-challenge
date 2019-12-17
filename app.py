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
latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
latest = dt.datetime.strptime(latest[0], '%Y-%m-%d')
year_earlier = latest - dt.timedelta(days=366)
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
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as the key and prcp as the value.
        Return the JSON representation of your dictionary."""

    #doesn't really specify what query to convert
    
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
    session = Session(engine)
    tobs_query = session.query(Measurement.date, Measurement.tobs).all()
    session.close()

    tobs_list = list(np.ravel(tobs_query))

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def t_start(start):
    session = Session(engine)
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    t_start_query = session.query(*sel).filter(Measurement.date >= start).all()
    session.close()
    t_start_list = list(np.ravel(t_start_query))
    return jsonify(t_start_list)

@app.route("/api/v1.0/<start>/<end>")
def t_start_end(start, end):
    session = Session(engine)
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    t_start_end_query = session.query(*sel).filter(Measurement.date.between(start, end)).all()
    session.close()
    t_start_end_list = list(np.ravel(t_start_end_query))
    return jsonify(t_start_end_list)

if __name__ == '__main__':
    app.run(debug=True)