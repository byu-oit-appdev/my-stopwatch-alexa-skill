#!/usr/bin/env python
#
# Copyright 2016 Brigham Young University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import time
import boto3
#import logging
from flask import Flask
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, '/')
#log = logging.getLogger()
# uncomment the following to see the JSON request / response structures pretty printed in the logs
# logging.getLogger('flask_ask').setLevel(logging.DEBUG)
app.config['DEBUG'] = False
app.config['ASK_APPLICATION_ID'] = 'amzn1.ask.skill.1925fb17-06d3-4803-b3a9-a73f7f251d7f' # enforce only this application can call
app.config['ASK_VERIFY_REQUESTS'] = True # verify requests are coming from Alexa
sdb = boto3.client('sdb')

@ask.launch
@ask.intent('StartIntent')
def start(startword=""):
    if not stopwatch_started():
        start_stopwatch()
        text = 'S. Watch started.'
        return statement(text).simple_card('Started', text)
    else:
        return statement('Your s watch is running and has already elapsed {}.'.format(get_current_duration()))

@ask.session_ended
@ask.intent('StopIntent')
@ask.intent('AMAZON.StopIntent')
def stop(stopword):
    if stopwatch_started():
        duration = stop_stopwatch()
        text = 'S. Watch ended.  {} have elapsed.'.format(duration)
        return statement(text).simple_card('Stopped', text)
    else:
        return statement("Your s watch hasn't started.")

@ask.intent('StatusIntent')
def status():
    if stopwatch_started():
        duration = get_current_duration()
        text = 'S. Watch running.  {} have elapsed.'.format(duration)
        return statement(text).simple_card('Status', text)
    else:
        return statement("Your s watch isn't running.")

@ask.intent('AMAZON.HelpIntent')
def help():
    text = 'S. Watch. You can start, stop or get the status for S. Watch. What would you like to do?'
    return question(text).simple_card('Help', text)

@ask.intent('CancelIntent')
@ask.intent('AMAZON.CancelIntent')
def stop(cancelword):
    stop_stopwatch()
    text = 'S. Watch canceled'
    return statement(text).simple_card('Canceled', text)

def stopwatch_started():
    result = sdb.get_attributes(DomainName='s-watch', ItemName=session.user.userId, ConsistentRead=True)
    return 'Attributes' in result

def start_stopwatch():
    sdb.put_attributes(DomainName='s-watch', ItemName=session.user.userId, Attributes=[{'Name': 'started', 'Value': str(int(time.time()))}])

def stop_stopwatch():
    duration = get_current_duration()
    sdb.delete_attributes(DomainName='s-watch', ItemName=session.user.userId)
    return duration

def get_current_duration():
    result = sdb.get_attributes(DomainName='s-watch', ItemName=session.user.userId, ConsistentRead=True)
    started_secs = int(result['Attributes'][0]['Value'])
    return humanize_time(int(time.time()) - started_secs)

def humanize_time(amount, units = 'seconds'):
    """
    From http://stackoverflow.com/a/26781642/3045
    """
    def process_time(amount, units):
        INTERVALS = [1, 60,
                     60*60,
                     60*60*24,
                     60*60*24*7,
                     60*60*24*7*4,
                     60*60*24*7*4*12,
                     60*60*24*7*4*12*100,
                     60*60*24*7*4*12*100*10]
        NAMES = [('second', 'seconds'),
                 ('minute', 'minutes'),
                 ('hour', 'hours'),
                 ('day', 'days'),
                 ('week', 'weeks'),
                 ('month', 'months'),
                 ('year', 'years'),
                 ('century', 'centuries'),
                 ('millennium', 'millennia')]
        result = []
        unit = map(lambda a: a[1], NAMES).index(units)
        # Convert to seconds
        amount = amount * INTERVALS[unit]
        for i in range(len(NAMES)-1, -1, -1):
            a = amount // INTERVALS[i]
            if a > 0:
                result.append( (a, NAMES[i][1 % a]) )
                amount -= a * INTERVALS[i]
        return result

    rd = process_time(int(amount), units)
    cont = 0
    for u in rd:
        if u[0] > 0:
            cont += 1
    buf = ''
    i = 0
    for u in rd:
        if u[0] > 0:
            buf += "%d %s" % (u[0], u[1])
            cont -= 1
        if i < (len(rd)-1):
            if cont > 1:
                buf += ", "
            else:
                buf += " and "
        i += 1
    return buf

if __name__ == '__main__':
    app.run(debug=True)
