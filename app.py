import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"-----------------------------------------------------------------------------------<br/>"
        f"All precipitation value for each specific date<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"-----------------------------------------------------------------------------------<br/>"
        f"List of Stations from the dataset<br/>"
        f"/api/v1.0/stations<br/>"
        f"-----------------------------------------------------------------------------------<br/>"
        f"Dates and temperature observations from a year from the last data point<br/>"
        f"/api/v1.0/tobs<br/>"
        f"-----------------------------------------------------------------------------------<br/>"
        f"list of the minimum, average and max temperature for a given start<br/>"
        f"/api/v1.0/start/<start><br/>"
        f"-----------------------------------------------------------------------------------<br/>"
        f"list of the minimum, average and max temperature for a given start-end range<br/>"
        f"/api/v1.0/start<start>/end<end><br/>"
        f"-----------------------------------------------------------------------------------<br/>"
    )

@app.route("/api/v1.0/precipitation")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all percipitation"""
    # Query all percipitation
    results = session.query(Measurement.station,Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).all()

    session.close()

    all_prcp = {}
    for i in range(len(results)):
        if results[i][1] != results[i-1][1]:
            all_prcp[results[i][1]]={}
            all_prcp[results[i][1]][results[i][0]] = results[i][2]
        else:
            all_prcp[results[i-1][1]][results[i][0]] = results[i][2]
    
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all percipitation"""
    # Query all stations
    results = session.query(Station.station,Station.name).group_by(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = []
    for station,name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all percipitation"""
    # Query all last year temperature
    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago =  dt.date(2017,8,23)- dt.timedelta(365)

    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.prcp).desc()).first()

    results = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.station == most_active_station[0]).\
        filter(Measurement.date <= last_day).\
        filter(Measurement.date >= year_ago).all()

    session.close()

    # Convert list of tuples into normal list
    last_year_temp = []
    for date,tobs in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        last_year_temp.append(temp_dict)

    return jsonify(last_year_temp)

@app.route("/api/v1.0/start/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all percipitation"""
    # Query temperature statistics from start date given
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).all()
    
    session.close()

    # Convert list of tuples into normal list
    startonly = {}
    for mi, ave, ma in results:
        startonly["Minimum Temperature"] = mi
        startonly["Average Temperature"] = ave
        startonly["Maximum Temperature"] = ma

    return jsonify(startonly)

@app.route("/api/v1.0/start<start>/end<end>")
def startend(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all percipitation"""
    # Query temperature statistics with start and end date
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    # Convert list of tuples into normal list
    startend = {}
    for mi, ave, ma in results:
        startend["Minimum Temperature"] = mi
        startend["Average Temperature"] = ave
        startend["Maximum Temperature"] = ma

    return jsonify(startend)
    
if __name__ == '__main__':
    app.run(debug=True)