# Import the dependencies.
import numpy as np

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
base = automap_base()
# reflect the tables
base.prepare(autoload_with=engine)

base.classes.keys()

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# Listing out all available routes
@app.route("/")
def welcome():
    """List all available api routs"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/after_Aug232016<br/>"
        f"/api/v1.0/Aug232016_thru_Sep232016"
    )

# Converting query results from precipiation analysis to a dictionary where 'date' is the key and 'prcp' is the value
# Returning the JSON of my dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    m_year = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date > '2016-08-23').\
        order_by(measurement.date).all()
    
    session.close()
    
    m_year_output = []
    for date, prcp in m_year:
        m_year_dict = {}
        m_year_dict[date] = prcp
        m_year_output.append(m_year_dict)

    return jsonify(m_year_output)

# Returning a JSON list of stations in the data
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    station_q = session.query(measurement.station).\
        group_by(measurement.station).all()
    
    session.close()

    station_output = list(np.ravel(station_q))

    return jsonify(station_output)

# Querying the dates and temperatures of the most active station for the previous year
# Returning the JSON list of the temperatures
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    active_temps = session.query(measurement.tobs).\
        filter(measurement.date > '2016-08-23').\
        filter(measurement.station == 'USC00519281').all()
    
    session.close()

    temp_output = list(np.ravel(active_temps))

    return jsonify(temp_output)

# Returning a JSON list of the min., max. and avg. temp. after 2016-08-23
@app.route("/api/v1.0/after_Aug232016")
def after_Aug232016():
    session = Session(engine)

    aug23_temps = [func.min(measurement.tobs),
                    func.max(measurement.tobs),
                    func.avg(measurement.tobs)]
    
    aug23_temps_q = session.query(*aug23_temps).\
        filter(measurement.date > '2016-08-23').all()
    
    session.close()

    aug23_temps_output = list(np.ravel(aug23_temps_q))

    return jsonify(aug23_temps_output)

# Returning a JSON list of the min., max. and avg. temp. between 2016-08-23 and 2016-09-23
@app.route("/api/v1.0/Aug232016_thru_Sep232016")
def Aug232016_thru_Sep232016():
    session = Session(engine)

    aug_sep_temps = [func.min(measurement.tobs),
                     func.max(measurement.tobs),
                     func.avg(measurement.tobs)]
                     
    aug_sep_q = session.query(*aug_sep_temps).\
        filter(measurement.date > '2016-08-23').\
        filter(measurement.date < '2016-09-24').all()
    
    session.close()

    aug_sep_output = list(np.ravel(aug_sep_q))

    return jsonify(aug_sep_output)

if __name__ == '__main__':
    app.run(debug=True)
