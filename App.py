# Dependencies
import numpy as np
import datetime as dt

# Python SQL Toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import Flask
from flask import Flask, jsonify

# Create Engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new mode
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#setup Flask
app = Flask(__name__)

#setup Flask routes
@app.route("/")
def Home():
    """Climate App!"""  

# List all routes that are available  
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end></br>"
        f"i.e. /api/v1.0/2016-08-23<br/>"
        f"i.e. /api/v1.0/2016-08-23/2017-08-23"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

# Start session
    session = Session(engine)

# Convert the query results to a dictionary using `date` as the key and `prcp` as the value 
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prcp_data = session.query(measurement.date, measurement.prcp).\
            filter(measurement.date >= year_ago).\
            order_by(measurement.date).all()
    prcp_datalist = dict(prcp_data)

# Close session
    session.close()

# Return the JSON representation of your dictionary
    return jsonify(prcp_datalist)

@app.route("/api/v1.0/stations")
def stations():

# Start session
    session = Session(engine)

    stations_all = session.query(measurement.station, station.name).\
                      filter(measurement.station == station.station).\
                      group_by(measurement.station).all()
    station_list = list(np.ravel(stations_all))

# Close session
    session.close()

# Return JSON List of Stations from the Dataset
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():

# Start session
    session = Session(engine)

# Query the dates and temperature observations of the most active station for the last year of data
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    temp_obs = session.query(measurement.date, measurement.tobs).\
            filter(measurement.date >= year_ago).\
            order_by(measurement.date).all()

    temp_obs_list = list(temp_obs)

# Close session
    session.close()

# Return a JSON list of temperature observations (TOBS) for the previous year
    return jsonify(temp_obs_list)

@app.route("/api/v1.0/<start>")
def start_day(start):

# Start session
    session = Session(engine)

# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
    start_day = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start).\
            group_by(measurement.date).all()
    
    calculate = []
    for date, min, avg, max in start_day:
        t_dict = {}
        t_dict["Date"] = date
        t_dict["TMIN"] = min
        t_dict["TAVG"] = avg
        t_dict["TMAX"] = max
        calculate.append(t_dict)

# Close session
    session.close()

# Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start Range
    return jsonify(calculate)

@app.route("/api/v1.0/<start>/<end>")
def start_end_day(start, end):

# Start session
    session = Session(engine)

# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive
    start_end_day = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start).\
            filter(measurement.date <= end).\
            group_by(measurement.date).all()
        
    recalculate = []
    for date, min, avg, max in start_end_day:
        rt_dict = {}
        rt_dict["Date"] = date
        rt_dict["TMIN"] = min
        rt_dict["TAVG"] = avg
        rt_dict["TMAX"] = max
        recalculate.append(rt_dict)

# Close session
    session.close()

# Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start-End Range
    return jsonify(recalculate)

if __name__ == '__main__':
    app.run(debug=True)