# app/science.py

import os
import pandas as pd
import numpy as np
import random
import math
import itertools

from sklearn import svm

from flask import current_app
from app.data import db, query_to_list
from app.sensors.models import Experiment, Sensor

"""
Support vector machines (SVMs) are a set of supervised learning methods 
used for classification, regression and outliers detection.
"""

_basedir = os.path.abspath(os.path.dirname(__file__))
UPLOADS = 'api/training'
UPLOAD_FOLDER = os.path.join(_basedir, UPLOADS)

"""
# LEGACY training data from phone
filename = '50_punches_labelled_pt1_pt2_combined.csv'
non_punch_filename = 'non_punch_pt1.csv'
non_punch_filename2 = 'non_punch_pt2.csv'
mix_filename = 'mix_labelled_pt1.csv'
"""

# NEW Training data from mbient

def to_setup():

    filename = 'MBIENT_straightPunch_chris.csv'
    filename2 = 'MBIENT_straightPunchtraining2_chris.csv'
    filename3 = 'MBIENT_straightPunchtraining3_chris.csv'
    filename4 = 'MBIENT_straightPunchtraining4_chris.csv'

    non_punch_filename = 'MBIENT_trainingGeneralMovement.csv'
    non_punch_filename2 = 'MBIENT_generalMotionTraining_chris.csv'
    non_punch_filename3 = 'MBIENT_gmt3.csv'

    hook_punch_filename = 'MBIENT_hookPunch_chris.csv'
    hook_punch_filename2 = 'MBIENT_hookpunchTraining_chris.csv'
    hook_punch_filename3 = 'MBIENT_hookpunchTraining2.csv'

    TRAIN_DATA = UPLOAD_FOLDER + '/punch/' + filename
    TRAIN_DATA4 = UPLOAD_FOLDER + '/punch/' + filename2
    TRAIN_DATA5 = UPLOAD_FOLDER + '/punch/' + filename3
    TRAIN_DATA10 = UPLOAD_FOLDER + '/punch/' + filename4
    TRAIN_DATA6 = UPLOAD_FOLDER + '/punch/' + hook_punch_filename
    TRAIN_DATA7 = UPLOAD_FOLDER + '/punch/' + hook_punch_filename2
    TRAIN_DATA8 = UPLOAD_FOLDER + '/punch/' + hook_punch_filename3

    TRAIN_DATA2 = UPLOAD_FOLDER + '/non_punch/' + non_punch_filename
    TRAIN_DATA3 = UPLOAD_FOLDER + '/non_punch/' + non_punch_filename2
    TRAIN_DATA9 = UPLOAD_FOLDER + '/non_punch/' + non_punch_filename3



# TEST_DATA = UPLOAD_FOLDER + '/labelled_test/' + mix_filename

def sql_to_pandas():
    pass

def pandas_cleanup(df):
    columns = []
    df_clean = df[['ACCELEROMETER_X', 'ACCELEROMETER_Y', 'ACCELEROMETER_Z', 'timestamp', 'experiment_id', 'Time_since_start']]
    return df_clean

columns = ['ACCELEROMETER_X',
            'ACCELEROMETER_Y',
            'ACCELEROMETER_Z',
            'GRAVITY_X',
            'GRAVITY_Y',
            'GRAVITY_Z',
            'LINEAR_ACCELERATION_X',
            'LINEAR_ACCELERATION_Y',
            'LINEAR_ACCELERATION_Z',
            'GYROSCOPE_X',
            'GYROSCOPE_Y',
            'GYROSCOPE_Z', 
            'MAGNETIC_FIELD_X',
            'MAGNETIC_FIELD_Y',
            'MAGNETIC_FIELD_Z',
            'ORIENTATION_Z',
            'ORIENTATION_X',
            'ORIENTATION_Y',
            'Time_since_start',
            'timestamp',
            'state']

            # SHOULD REMOVE THE STATE COLUMN FOR NON TEST DATA

def clean_up(df):
    clean_df = pd.DataFrame(df.index.tolist(), columns=['ACCELEROMETER_X', 'ACCELEROMETER_Y', 'ACCELEROMETER_Z'])
    clean_df = clean_df.applymap(str)
    clean_df = clean_df.apply(lambda s: s.str.replace('(', ''))
    clean_df = clean_df.apply(lambda s: s.str.replace(')', ''))
    clean_df = clean_df.reindex(columns=columns)
    return clean_df

def set_straight_punch(the_df):
    the_df['state'] = 1
    punch_final_df = the_df
    return punch_final_df

def set_non_punch(my_df):
    my_df['state'] = 0
    non_punch_final_df = my_df
    return non_punch_final_df

def set_hook_punch(hook_df):
    hook_df['state'] = 2
    hook_punch_final_df = hook_df
    return hook_punch_final_df


def more_setup():
    df_punch = pd.read_csv(TRAIN_DATA, skiprows=[0], names=['initial'])
    df_punch = clean_up(df_punch)
    df_punch = set_straight_punch(df_punch)

    df_punch2 = pd.read_csv(TRAIN_DATA4, skiprows=[0], names=['initial'])
    df_punch2 = clean_up(df_punch2)
    df_punch2 = set_straight_punch(df_punch2)

    df_punch3 = pd.read_csv(TRAIN_DATA5, skiprows=[0], names=['initial'])
    df_punch3 = clean_up(df_punch3)
    df_punch3 = set_straight_punch(df_punch3)

    df_punch4 = pd.read_csv(TRAIN_DATA10, skiprows=[0], names=['initial'])
    df_punch4 = clean_up(df_punch4)
    df_punch4 = set_straight_punch(df_punch4)

    df_hook_punch = pd.read_csv(TRAIN_DATA6, skiprows=[0], names=['initial'])
    df_hook_punch = clean_up(df_hook_punch)
    df_hook_punch = set_hook_punch(df_hook_punch)

    df_hook_punch2 = pd.read_csv(TRAIN_DATA7, skiprows=[0], names=['initial'])
    df_hook_punch2 = clean_up(df_hook_punch2)
    df_hook_punch2 = set_hook_punch(df_hook_punch2)

    df_hook_punch3 = pd.read_csv(TRAIN_DATA8, skiprows=[0], names=['initial'])
    df_hook_punch3 = clean_up(df_hook_punch3)
    df_hook_punch3 = set_hook_punch(df_hook_punch3)

    df_non_punch2 = pd.read_csv(TRAIN_DATA2, skiprows=[0], names=['initial'])
    df_non_punch2 = clean_up(df_non_punch2)
    df_non_punch2 = set_non_punch(df_non_punch2)

    df_non_punch3 = pd.read_csv(TRAIN_DATA9, skiprows=[0], names=['initial'])
    df_non_punch3 = clean_up(df_non_punch3)
    df_non_punch3 = set_non_punch(df_non_punch3)

    df_non_punch = pd.read_csv(TRAIN_DATA3, skiprows=[0], names=['initial'])
    df_non_punch = clean_up(df_non_punch)
    df_non_punch = set_non_punch(df_non_punch)

    df_train = pd.concat([df_punch, df_punch2, df_punch3, df_punch4, df_hook_punch, df_hook_punch2, df_hook_punch3, df_non_punch2, df_non_punch3, df_non_punch], ignore_index=True)
    # df_test = pd.read_csv(TEST_DATA, skiprows=[0], names=columns)

def my_svm(id):

    """
    As other classifiers, SVC, NuSVC and LinearSVC take as input two arrays:
    an array X of size [n_samples, n_features] holding the training samples, 
    and an array y of class labels (strings or integers), size [n_samples]:
    """
    #=============================
    #TRAINING - TODO: MOVE THIS!!!
    #=============================


    x1 = df_train['ACCELEROMETER_X'].values
    x2 = df_train['ACCELEROMETER_Y'].values
    x3 = df_train['ACCELEROMETER_Z'].values

    y = df_train['state'].values
    X = np.column_stack([x1, x2, x3])

    clf = svm.SVC()
    clf.fit(X, y)

    #=============================
    # RUN DATA AGAINST THE MODEL
    #=============================

    # Load the pandas dataframe from the DB using the experiment id
    pandas_id = id
    current_app.logger.debug('Preparing to make prediction for experiment: {}'.format(pandas_id))

    query = db.session.query(Sensor).filter(Sensor.experiment_id == pandas_id)
    df = pd.read_sql_query(query.statement, query.session.bind)

    _x1 = df['ACCELEROMETER_X'].values
    _x2 = df['ACCELEROMETER_Y'].values
    _x3 = df['ACCELEROMETER_Z'].values

    _X = np.column_stack([_x1, _x2, _x3])

    my_prediction = clf.predict(_X)
    prediction_df = pd.DataFrame(my_prediction, columns=['prediction'])

    prediction_df = prediction_df.replace(to_replace="1", value="straight punch") # 1 = straight punch
    prediction_df = prediction_df.replace(to_replace=2, value="hook punch") # 2 = hook punch
    prediction_df = prediction_df.replace(to_replace=0, value="other") # to check, why is 0 not a string?
    df['prediction'] = prediction_df['prediction']

    current_app.logger.debug('DF length is: {}, which should match the number of predictions: {}'.format(len(df), len(prediction_df)))
    prediction_input2 = df.values.tolist()

    for obj, new_value in itertools.izip(query, prediction_input2):
        obj.prediction = new_value[22] # 22nd column is the prediction
        db.session.add(obj)
   
    db.session.commit()

    return 'prediction made'

def check_sequence(dataframe, index_value):
    is_punch = []
    punch = ('straight punch','hook punch')
    prev_value = index_value - 1
    n_2 = index_value - 2
    n_3 = index_value - 3
    n_4 = index_value - 4

    next_value = index_value + 1
    n2 = index_value + 2
    n3 = index_value + 3
    n4 = index_value + 4
    n5 = index_value + 5
    n6 = index_value + 6
    n7 = index_value + 7
    n8 = index_value + 8
    n9 = index_value + 9
    n10 = index_value + 10
    

    forward_chain = [next_value, n2, n3, n4, n5, n6, n7, n8, n9, n10]
    back_chain = [prev_value, n_2, n_3, n_4]

    for f_value in forward_chain:
        if (dataframe[f_value] not in punch):
            is_punch.append(True)
        else: 
            is_punch.append(False)

    for b_value in back_chain:
        if (dataframe[b_value] in punch):
            is_punch.append(True)
        else:
            is_punch.append(False)

    if False in is_punch:
         return False
    else: 
        print 'punch detected for: {}'.format(index_value)
        return True
        

def count_calculator(df):
    """
    takes the ML predictions and attempts to distinguish individual
    motions (in this case punches) from the patterns therein
    """
    print type(df)
    print len(df)

    counter = 0

    # ========================================================
    # Look for a sequence of 3 straight punches in a row to 
    # signify the beginning of a single punch
    # ========================================================
    try: 
        sp_values = df[df == 'straight punch'].index
        print 'number of straight punch values {}'.format(len(sp_values))

        # This gets us the index of the first straight punch value
        first_value = df[df == 'straight punch'].index[0]
        print first_value

    except Exception as e:
        current_app.logger.debug('Error calculating punch numbers: {}'.format(e))
        counter = 0

    # loop through all the indices of punches
    for value in sp_values:
        tick = check_sequence(df, value)
        if tick == True:
            counter += 1

    return counter

