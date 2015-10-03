import os, csv
import json
from time import mktime
from datetime import datetime
from numpy import genfromtxt
import pandas as pd

from flask import abort, Blueprint, flash, jsonify, Markup, redirect, render_template, request, Response, \
url_for, session
from random import choice
from flask.ext.login import current_user, login_required

from .forms import SiteForm, VisitForm
from .models import Site, Visit, Sensor, Experiment
from app.data import query_to_list, db
from app.science import sql_to_pandas, pandas_cleanup

from werkzeug import secure_filename


sensors = Blueprint("sensors", __name__, static_folder='static', template_folder='templates')


ALLOWED_EXTENSIONS = set(['txt', 'csv'])
UPLOAD_FOLDER = os.path.realpath('.')+'/app/uploads'

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def Load_Data(file_name):
    # data = genfromtxt(file_name, delimiter=',', skiprows=1)
    data = pd.read_table(file_name, header=None, skiprows=1, delimiter=',') 
    return data.values.tolist()

class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)




@sensors.route("/")
@sensors.route("/index")
def index():
    # site_form = SiteForm()
    # visit_form = VisitForm()
    return render_template("index.html")



@sensors.route('/csv', methods=['GET', 'POST'])
def csv_route():
    if request.method == 'GET':
        return render_template('sensors/csv.html')
    elif request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            my_experiment = Experiment(hardware='Nexus5', t_stamp=datetime.now())
            db.session.add(my_experiment)
            db.session.commit()

            try:
                file_name = filename
                data = Load_Data(os.path.join(UPLOAD_FOLDER, file_name))
                count = 0 

                for i in data:
                    u = Experiment.query.get(1)
                    my_timestamp = datetime.strptime(i[3], "%Y-%m-%d %H:%M:%S:%f")
                    el_sensor = Sensor(**{
                        'accelerometer_x' : i[0],
                        'accelerometer_y' : i[1],
                        'accelerometer_z' : i[2],
                        'timestamp' : my_timestamp,
                        'experiment' : my_experiment
                    })
                    
                    db.session.add(el_sensor)
                    count += 1

                if ((count % 10 == 0) | (count < 20)):
                    db.session.commit() #Attempt to commit all the records
                 
            except Exception as e:
                print e
                db.session.rollback() #Rollback the changes on error
            finally:
                pass
                # db.session.close() #Close the connection
            
            # Test change for Urs
            flash("CSV data saved to DB") 
            return redirect(url_for('sensors.complete')), 201
        else:
            return render_template('index.html'), 400
    else:
        return '404'

@sensors.route('/complete')
def complete():
     return render_template('sensors/complete.html')

@sensors.route('/display')
def display():
    sql_to_pandas() # TODO prep/check function
    names = os.listdir(UPLOAD_FOLDER)
    query = db.session.query(Sensor)
    df = pd.read_sql_query(query.statement, query.session.bind)
    db_index = pd.unique(df.experiment_id.values)
    return render_template('sensors/show_files.html', file_url=names, db_index=db_index)

@sensors.route('/display/<int:id>')
def display_id(id):
    query = db.session.query(Sensor)
    df = pd.read_sql_query(query.statement, query.session.bind)
    pandas_id = id
    df2 = df[df.experiment_id == pandas_id]
    db_index_choice = df2
    experiment_number = pd.unique(df2.experiment_id.values)
    return render_template('sensors/file_details.html', experiment_number=experiment_number[0], 
        db_index_choice=db_index_choice.to_html(), id=id)

@sensors.route('/display/<int:id>/graph')
def display_graph(id):

    query = db.session.query(Sensor)
    temp_df = pd.read_sql_query(query.statement, query.session.bind)
    
    # remove duplicate index values for json dump
    df = pandas_cleanup(temp_df) 
    
    pandas_id = id
    df2 = df[df.experiment_id == pandas_id]
    db_index_choice = df2
    experiment_number = pd.unique(df2.experiment_id.values)

    print df

    d3_json = df.to_json(orient='records')

    d3_response = json.dumps(d3_json)


    return render_template('sensors/file_graph.html', experiment_number=experiment_number[0], 
        db_index_choice=db_index_choice.to_html(), id=id, d3_response = d3_response)

