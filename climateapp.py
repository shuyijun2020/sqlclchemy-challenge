
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

#Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
measurement = Base.classes.measurement
station = Base.classes.station
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    return (
        f"Welcome to Hawaii!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start><br/>"
        f"/api/v1.0/temp/<start>/<end><br/>"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    #Return the JSON representation of your dictionary.
    session = Session(engine)
    oneyear = dt.date(2017,8,23)-dt.timedelta(days=365)
    oneyear_query = session.query(
        measurement.date, measurement.prcp).filter(measurement.date>=oneyear).\
        order_by(measurement.date).all()
    session.close()
    dt_prcp =[]
    for dtprcp in oneyear_query:
        dtprcp_dict = {}
        dtprcp_dict["date"] = dtprcp.date
        dtprcp_dict["prcp"] = dtprcp.prcp
        dt_prcp.append(dtprcp_dict)
    return jsonify(dt_prcp)
    #note: return jsonify(dict(oneyear_query)) also works - output more like csv

    # The followings are not working
    # for date, prcp in oneyear_query:
    #     measurement_dict = {}
    #     measurement_dict["date"] = date
    #     measurement_dict["prcp"] = prcp


@app.route("/api/v1.0/stations")
# def stations():
#     #Return a JSON list of stations from the dataset.
#     session = Session(engine)
#     station_query = session.query(
#     station.id, station.station, station.name, station.latitude, station.longitude,station.elevation).all()  
        
#     session.close()
    # stations =[]
    # for stations in station_query:
    #     stations_dict = {}
    #     stations_dict["id"] = stations.id
    #     stations_dict["station"] = stations.station
    #     stations_dict["name"] = stations.name
    #     stations_dict["latitude"] = stations.latitude
    #     stations_dict["longitude"] = stations.longitude
    #     stations_dict["elevation"] = stations.elevation

    #     stations.append(stations_dict)
    # return jsonify(dict(station_query))

def stations():
    session.query(measurement.station).distinct().count()
    active_stations = session.query(measurement.station,func.count(measurement.station)).\
                               group_by(measurement.station).\
                               order_by(func.count(measurement.station).desc()).all()
    
    act_station = []
    for stat in active_stations:
        stat_dict = {}
        stat_dict["station"] = stat.station
        act_station.append(stat_dict)

    return jsonify(act_station)


@app.route("/api/v1.0/tobs")
def dttobs():
    #Query the dates and temperature observations of the most active station for the last year of data.
    #Return a JSON list of temperature observations (TOBS) for the previous year.

    session = Session(engine)
    oneyear = dt.date(2017,8,23)-dt.timedelta(days=365)
    oneyeartobsmostactive = session.query(measurement.date, measurement.tobs).\
                        filter(measurement.date>=oneyear).\
                        filter(measurement.station == 'USC00519281').all()
  
    session.close()
    dt_tobs = []
    for dttobs in oneyeartobsmostactive:
        dttobs_dict = {}
        dttobs_dict["date"] = dttobs.date
        dttobs_dict["tobs"] = dttobs.tobs
        dt_tobs.append(dttobs_dict)
    return jsonify(dt_tobs)

def calc_start_temps(start_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()


@app.route("/api/v1.0/<start>")

#Return a JSON list of the min, avg, and max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive

def start_date(start):
    calc_start_temp = calc_start_temps(start)
    temp= list(np.ravel(calc_start_temp))

    Tmin = t_temp[0]
    Tmax = t_temp[2]
    Tavg = t_temp[1]
    Tdict = {'Minimum temperature': Tmin, 'Maximum temperature': Tmax, 'Avg temperature': Tavg}

    return jsonify(Tdict)

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
    start_date (string): A date string in the format %Y-%m-%d
    end_date (string): A date string in the format %Y-%m-%d
    Returns:
    TMIN, TAVE, and TMAX
    """
    return session.query(func.min(measurement.tobs), \
                         func.avg(measurement.tobs), \
                         func.max(measurement.tobs)).\
                         filter(measurement.date >= start_date).\
                         filter(measurement.date <= end_date).all()

@app.route("/api/v1.0/<start>/<end>")

def start_end_date(start, end):
    
    calc_temp = calc_temps(start, end)
    ta_temp= list(np.ravel(calc_temp))

    tmin = ta_temp[0]
    tmax = ta_temp[2]
    temp_avg = ta_temp[1]
    temp_dict = { 'Minimum temperature': tmin, 'Maximum temperature': tmax, 'Avg temperature': temp_avg}

    return jsonify(temp_dict)


 
if __name__ == "__main__":
    app.run(debug=True)



