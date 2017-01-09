import os
from flask import Flask, url_for, jsonify, request, make_response
from celery import Celery, states
from flask_cors import CORS, cross_origin

import numpy as np
import pandas as pd


app = Flask(__name__)
CORS(app)

app.config['CELERY_BROKER_URL'] = 'amqp://admin:password@localhost/test'
app.config['CELERY_RESULT_BACKEND'] = 'amqp://admin:password@localhost/test'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@app.route('/upload', methods=['POST'])
def upload():
    file_obj = request.files.get('file')
    file_name = file_obj.filename

    path = os.path.join('./uploads', file_name)

    file_obj.read(0)

    try:
        file_obj.save(path)
    except IOError:
        print 'I/O Error'

    file_obj.close()

    file_task = read_csv_task.apply_async(args=[path])

    return make_response(jsonify({'task_id': file_task.task_id}))

@app.route('/task/<task_id>', methods=['GET'])
def check_task_status(task_id):

    task = read_csv_task.AsyncResult(task_id)
    state = task.state
    response = {}
    response['state'] = state

    if state == states.SUCCESS:
        response['result'] = task.get()
    elif state == states.FAILURE:
        try:
            response['error'] = task.info.get('error')
        except Exception as e:
            response['error'] = 'Unknown error occurred'
        
    return make_response(jsonify(response))


@celery.task(bind=True)
def read_csv_task(self, path):

    self.update_state(state=states.PENDING)

    df = pd.read_csv(path)
    result = compute_properties(df)
    
    return result

def compute_properties(df):
    properties = {}

    properties['num_rows'] = len(df)
    properties['num_columns'] = len(df.columns)

    properties['column_data'] = get_column_data(df)

    return properties

def get_column_data(df):
    result = []

    for c in df:
        info = {}
        col = df[c]

        info['name'] = c
        info['num_null'] = col.isnull().sum()

        if col.dtypes == 'int64':
            info['mean'] = np.mean(col)
            info['median'] = np.median(col)
            info['stddev'] = np.std(col)
            info['min'] = col.min()
            info['max'] = col.max()
        else:
            unique_values = col.unique().tolist()
            print len(unique_values), len(df)
            if len(unique_values) < len(df):
                info['unique_values'] = unique_values
            else:
                info['unique_values'] = True

        result.append(info)

    return result

if __name__ == '__main__':
    app.run(port=8889, debug=True)

