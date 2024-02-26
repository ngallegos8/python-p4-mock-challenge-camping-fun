#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''

class CampersAll(Resource):

    def get(self):
        try:
            campers = [camper.to_dict(only=("id", "name", "age")) for camper in Camper.query.all()]
            return campers, 200
        except:
            return {"error": "Bad request"}, 400

    
    def post(self):

        data = request.get_json()
        try:
            new_camper = Camper(
                name = data['name'],
                age = data['age']
            )
            db.session.add(new_camper)
            db.session.commit()

            return new_camper.to_dict(only=("id", "name", "age")), 201
        except:
            return { "errors": ["validation errors"] }, 400

api.add_resource(CampersAll, '/campers')



class CamperByID(Resource):
        
    def get(self, id):
        try: 
            camper = Camper.query.filter(Camper.id == id).first()
            return camper.to_dict(only=("id", "name", "age", "activities")), 200
        except: 
            return {"error": "Camper not found"}, 404
        
    def patch(self, id):
        try:
            data = request.get_json()
            camper = Camper.query.filter(Camper.id==id).first()
            for attr in data:
                setattr(camper, attr, data[attr])
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict(only=("id", "name", "age")), 202
        except:
            return {"errors": ["validation errors"]}

api.add_resource(CamperByID, '/campers/<int:id>')



class ActivitiesAll(Resource):

    def get(self):
        try:
            activities = [activity.to_dict() for activity in Activity.query.all()]
            return activities, 200
        except:
            return {'error': 'Bad request'}, 400

    
api.add_resource(ActivitiesAll, '/activities')



class ActivityByID(Resource):

    def delete(self, id):
        try:
            activity = Activity.query.filter(Activity.id == id).first()
            db.session.delete(activity)
            db.session.commit()
            return {}, 204
        except: 
            return {"error": "Activity not found"}, 404

    
api.add_resource(ActivityByID, '/activities<int:id>')



class SignupsAll(Resource):
    
    def post(self):
        try:
            data = request.get_json()
            new_signup = Signup(
                camper_id = data['camper_id'],
                activity_id = data['activity_id'],
                time = data['time']
            )
            db.session.add(new_signup)
            db.session.commit()
            return new_signup.activity.to_dict(), 201
        except:
            return { "errors": ["validation errors"] }, 400
    
api.add_resource(SignupsAll, '/signups')





if __name__ == '__main__':
    app.run(port=5555, debug=True)
