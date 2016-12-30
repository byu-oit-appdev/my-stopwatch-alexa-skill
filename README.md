# S Watch Alexa Skill
A serverless stopwatch Alexa Skill using Amazon Lambda, zappa, flask-adk and Amazon Simpledb.

# Usage
* Say, "Alexa, enable S Watch"
* Then, to start the stopwatch say, "Alexa, Start S Watch"
* To stop the stopwatch and hear how long it was running say, "Alexa, tell S Watch to end"

# Developing
* clone the repo
* make sure you have python2.7 and the awscli installed
* run `aws sdb create-domain --domain-name s-watch`
* run `python -m virtualenv venv`
* run `source venv/bin/activate`
* run `python -m pip install -r requirements.txt`
* edit zappa_settings.json changing manage_roles to true
* run `zappa deploy production`
* edit zappa_settings.json changing manage_roles to false
* add the following to your zappa-permissions IAM policy that zappa created in the Statement array
```
        {
            "Effect": "Allow",
            "Action": [
                "sdb:*"
            ],
            "Resource": "arn:aws:sdb:us-west-2:<your AWS account id goes here>:domain/s-watch"
        },
```
* set up your alexa skills application at https://developer.amazon.com/edw/home.html
 * in the Interation Model section fill in the values from the intent_schema.json, custom_slot_types.txt and sample_utterances.txt files respectively.
 * in the Configuration section choose the HTTPS Endpoint type
 * in the SSL Certificate section choose 'My development endpoint is a sub-domain of a domain that has a wildcard certificate from a certificate authority'
* update this line of code in app.py to `app.config['ASK_APPLICATION_ID'] = '<your alexa application id goes here>'`
* update the code by running `zappa update production`
* to undeploy the code run `zappa undeploy production`

icon from https://commons.wikimedia.org/wiki/File:Simpleicons_Business_stopwatch.svg
