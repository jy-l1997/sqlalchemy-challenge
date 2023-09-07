# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hwaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    return (f"Available pages: <br/>"
            f"/api/v1.0/precipitation"
            f"/api/v1.0/stations"
            f"/api/v1.0/tobs"
            f"/api/v1.0/<start>"
            f"/api/v1.0/<start>/<end>"
           )

@app.route("/api/v1./precipitation")
def precipitation():
    session = Session(engine)
    
    one_year_prev= dt.date(2017,8,23) - dt.timedelta(days = 365)
    results = session.query(Measurement.date, Measurement.prcp) \
                    .filter(Measurement.date >= one_year_prev).all()
        
    session.close()
    
    date_precip = {}
    for (k,v) in results:
        date_precip[k] = v
    
    return jsonify(date_precip)
    
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    
    station_list = []
    for x in results:
        station_list.append(x[0])
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    active_stations = session.query(Measurement.station,func.count(Measurement.station)) \
                            .group_by(Measurement.station) \
                            .order_by(func.count(Measurement.station).desc()) \
                            .all()
    most_active = active_stations[0][0]
    results = session.query(Measurement.tobs) \
                    .filter(Measurement.station == most_active) \
                    .all()
    session.close()
    
    tobs_list = []
    for x in results:
        tobs_list.append(x[0])
        
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    start_date = dt.date(start)
    results = session.query(Measurement.tobs) \
                .filter(Measurement.date >= start_date) \
                .all()
    session.close()
    
    temp_df = pd.DataFrame(results)
    temp_min = min(temp_df['tobs'])
    temp_max = max(temp_df['tobs'])
    temp_avg = round(np.mean(temp_df['tobs']),1)
        
    return jsonify(temp_min, temp_max, temp_avg)

@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    session = Session(engine)
    start_date = dt.date(start)
    end_date = dt.date(end)
    results = session.query(Measurement.tobs) \
                .filter(start_date <= Measurement.date <= end_date) \
                .all()
    session.close()
    
    temp_df = pd.DataFrame(results)
    temp_min = min(temp_df['tobs'])
    temp_max = max(temp_df['tobs'])
    temp_avg = round(np.mean(temp_df['tobs']),1)
        
    return jsonify(temp_min, temp_max, temp_avg)