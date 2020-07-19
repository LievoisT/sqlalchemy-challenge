from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import pandas as pd
import numpy as np
import datetime as dt


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    print("home req")
    return "Available routes: /precipitation, /stations, /tobs, /start=, /start=/end="

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    
    all_prcp = []
    for date, precip in results:
           mdict = {}
           mdict["date"] = date
           mdict["prcp"] = precip
           all_prcp.append(mdict)
    return jsonify(all_prcp)
           
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    busiest_id = session.query(Measurement.station).\
    group_by(Measurement.station).\
    order_by(func.count().desc()).first()[0]

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > dt.date.fromisoformat(last_date) - dt.timedelta(days=365)).\
        filter(Measurement.station == busiest_id).all()
    
    session.close()

    all_tobs = []
    for date, tob in results:
        tdict = {}
        tdict["date"] = date
        tdict["tobs"] = tob
        all_tobs.append(tdict)
    
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>/")
def startroute(start):
    session = Session(engine)

    startdt = dt.date.fromisoformat(start)

    tobsdict = {}
    tobsdict["TMIN"] = session.query(Measurement.date, func.min(Measurement.tobs)).\
        filter(Measurement.date > startdt).all()[0][1]
    
    tobsdict["TAVG"] = session.query(Measurement.date, func.avg(Measurement.tobs)).\
        filter(Measurement.date > startdt).all()[0][1]

    tobsdict["TMAX"] = session.query(Measurement.date, func.max(Measurement.tobs)).\
        filter(Measurement.date > startdt).all()[0][1]

    session.close()

    return jsonify(tobsdict)


@app.route("/api/v1.0/<start>/<end>/")
def startend(start, end):

    session = Session(engine)

    start = dt.date.fromisoformat(start)
    end = dt.date.fromisoformat(end)

    tobsdict = {}
    tobsdict["TMIN"] = session.query(Measurement.date, func.min(Measurement.tobs)).\
        filter(Measurement.date > start).\
        filter(Measurement.date < end).all()[0][1]
    
    tobsdict["TAVG"] = session.query(Measurement.date, func.avg(Measurement.tobs)).\
        filter(Measurement.date > start).\
        filter(Measurement.date < end).all()[0][1]

    tobsdict["TMAX"] = session.query(Measurement.date, func.max(Measurement.tobs)).\
        filter(Measurement.date > start).\
        filter(Measurement.date < end).all()[0][1]

    session.close()

    return jsonify(tobsdict)


if __name__ == "__main__":
    app.run(debug=True)