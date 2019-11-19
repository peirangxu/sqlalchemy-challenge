import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from collections import defaultdict
from itertools import chain

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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/date<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all percipitation"""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()

    session.close()

    
    all_prcp = []
    for date,prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)
    dd = defaultdict(list)
    for i in range(len(all_prcp)):
        for j,k in chain(all_prcp[i].items()):
            dd[j].append(k)
    
    return jsonify(dd)
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all percipitation"""
    # Query all passengers
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
    # Query all passengers
    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago =  dt.date(2017,8,23)- dt.timedelta(365)

    results = session.query(Measurement.date,Measurement.tobs).\
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

@app.route("/api/v1.0/<date>")
def start(date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all percipitation"""
    # Query all passengers
    date = "2017-01-01"
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= date).all()
    
    session.close()

    # Convert list of tuples into normal list
    startonly = list(np.ravel(results))

    return jsonify(startonly)

@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all percipitation"""
    # Query all passengers
    start = "2017-01-01"
    end = "2017-02-02"
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    # Convert list of tuples into normal list
    startend = list(np.ravel(results))

    return jsonify(startend)

if __name__ == '__main__':
    app.run(debug=True)