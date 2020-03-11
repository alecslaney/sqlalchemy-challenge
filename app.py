import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

year_ago = '2016-08-23'
most_active_station = 'USC00519281'

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"The Great Hawaii Weather API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/DATE (Format date yyyyMMdd)<br/>"
        f"/api/v1.0/EARLIEST-DATE/LATEST-DATE (Format date yyyyMMdd/yyyyMMdd, earliest date first)<br/>"
    )

# Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
@app.route("/api/v1.0/precipitation")
def precip():
    precip_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).\
    group_by(Measurement.date).all()

    return jsonify(precip_data)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations_data = session.query(Station.station, Station.name).order_by(Station.name).all()

    return jsonify(stations_data)

# Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    tobs_data = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
    filter(Measurement.station == most_active_station).filter(Measurement.date >= year_ago).all()
    
    return jsonify(tobs_data)

# Return a JSON list of the minimum temperature, the average temperature, 
# and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/<date>")
def temp(date):
    date_tob_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= date).all()
    
    return jsonify(date_tob_data)

@app.route("/api/v1.0/<date1>/<date2>")
def temps(date1, date2):
    dates_tob_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= date1).filter(Measurement.date <= date2).all()
    
    return jsonify(dates_tob_data)

if __name__ == "__main__":
    app.run(debug=True)