from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from secret import my_password
from marshmallow import fields
from marshmallow import ValidationError


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/fitness_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    age = fields.Integer(required=True)
    
    class Meta:
        fields = ("member_id","name", "age")
        
member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

class SessionSchema(ma.Schema):
    member_id = fields.Int(required=False)
    
    date = fields.Date(required=True)
    duration_minutes = fields.Integer(required=True)
    calories_burned = fields.Integer(required=True)
    
    class Meta:
        fields = ("session_id","member_id", "date", "duration_minutes", "calories_burned")
        
session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True)

class Member(db.Model):
    __tablename__ = 'member'
    member_id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    workoutsessions = db.relationship('WorkoutSession', backref='member')
    
    
class WorkoutSession(db.Model):
    __tablename__ = 'workout_sessions'
    session_id = db.Column(db.Integer,primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Integer, nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.member_id'))
    
@app.route('/member', methods=['GET'])
def get_members():
    members = Member.query.all()
    return members_schema.jsonify(members)

@app.route('/member', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    new_member = Member(name=member_data['name'], age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "New member added successfully"}),201

@app.route('/member/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    member = Member.query.get_or_404(member_id)#retrieves the Member record with the primry key(member_id). If not found raises a 404 error
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400

    #member.member_id = member_data['member_id']
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({"Message": "Member details updated successfully"}),200

@app.route('/member/<int:member_id>',methods=['DELETE'])
def delete_member(member_id):
    try:
        member = Member.query.get_or_404(member_id)
        db.session.delete(member)
        db.session.commit()
        return jsonify({"Message": "Member removed successfully"}),200
    except Exception as e: 
        return jsonify({"Error": str(e)}), 500    
    
    
    
@app.route('/workout_session/<int:member_id>', methods=['GET'])
def get_sessions(member_id):
    session = WorkoutSession.query.filter_by(member_id).all()
    return sessions_schema.jsonify(session)

@app.route('/workout_session/<int:member_id>', methods=['POST'])
def add_session(member_id):
    try:
        session_data = session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    # member = db.session.get(member_id)# getting all the information of the member from the member id in the database and tying it to this variable member. converts all the info to use in python
    # new_session = WorkoutSession(date=session_data['date'], duration_minutes=session_data['duration_minutes'], calories_burned=session_data['calories_burned'])
    
    # member.workoutsessions.append(new_session)#This all of the member's information stored into member. workoutsessions is the propery of the Member class which holds all of the workoutsessions that are tied to that member. appending new session to the member
    db.session.add(member)#adding it to the sqlalchemy session .. staging the info
    db.session.commit()#commiting the information then sqlachemy will do its magic
    return jsonify({"Session added successfully"}),201
    
    # db.session.commit()
    # return jsonify({"message": "New session added successfully"}),201

@app.route('/workout_session/<int:id>', methods=['PUT'])
def update_session(session_id):
    session = WorkoutSession.query.get_or_404(session_id)
    try:
        session_data = session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    
    session.date = session_data['date']
    session.duration_minutes = session_data['duration_minutes']
    session.calories_burned = session_data['calories_burned']
    db.session.commit()
    return jsonify({"Message": "Session details updated successfully"}),200

@app.route('/workout_session/<int:session_id>',methods=['DELETE'])
def delete_session(session_id):
    try:
        session = WorkoutSession.query.get_or_404(session_id)
        db.session.delete(session)
        db.session.commit()
        return jsonify({"Message": "Session removed successfully"}),200
    except Exception as e: 
        return jsonify({"Error": str(e)}), 500        
    
        
with app.app_context():
    db.create_all()
    
if __name__ == '__main__':
    app.run(debug=True)
