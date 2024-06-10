#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
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

class Scientists(Resource):
    def get(self):
        scientists = Scientist.query.all()
        return jsonify([s.to_dict(rules=('-missions',)) for s in scientists])
    
    def post(self):
        try: 
            data = request.get_json()
            scientist = Scientist(name=data["name"], field_of_study=data["field_of_study"])
            db.session.add(scientist)
            db.session.commit()
            return make_response(scientist.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
            
    

class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            return jsonify(scientist.to_dict())
        else:
            return make_response(jsonify({"error": "Scientist not found"}), 404)
    
    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            try: 
                data = request.get_json()
                for attr in data:
                    setattr(scientist, attr, data[attr])
                db.session.add(scientist)
                db.session.commit()
                return make_response(scientist.to_dict(), 202)
            except ValueError:
                return make_response({"errors": ["validation errors"]}, 400)
        else:
            return make_response(jsonify({"error": "Scientist not found"}), 404)

    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            return make_response({"message": "Scientist deleted"}, 204)
        else:
            return make_response(jsonify({"error": "Scientist not found"}), 404)
        
class Planets(Resource):
    def get(self):
        planets = Planet.query.all()
        return jsonify([p.to_dict(rules=('-missions',)) for p in planets])
    
class Missions(Resource):
    def get(self):   
        missions = Mission.query.all()
        return jsonify([m.to_dict(rules=('-planet',)) for m in missions])
    
    def post(self):
        try:
            data = request.get_json()
            mission = Mission(
                name=data["name"],
                scientist_id=data["scientist_id"],
                planet_id=data["planet_id"]
                )
            db.session.add(mission)
            db.session.commit()
            return make_response(mission.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
        
api.add_resource(Missions, '/missions', endpoint='missions')
api.add_resource(Planets, '/planets', endpoint='planets')
api.add_resource(ScientistById, '/scientists/<int:id>')
api.add_resource(Scientists, '/scientists', endpoint='scientists')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
