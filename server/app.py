from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)
#enable flask_restful
api = Api(app)

# @app.route('/messages')
# def messages():
#     return ''

# @app.route('/messages/<int:id>')
# def messages_by_id(id):
#     return ''

class AllMessages(Resource):
    def get(self):
        q = Message.query.order_by('created_at').all()
        if(not q):
            return make_response({'message': '/messages not found'}, 404)
        return make_response([m.to_dict() for m in q], 200)

    def post(self):
        #import ipdb; ipdb.set_trace()
        try:
            # get json from request
            data = request.get_json()

            # create new message instance
            new_message = Message(body=data.get("body"), username=data.get("username"))
            # add and commit to db 
            
            db.session.add(new_message)
            db.session.commit()
        except:
            # error if something goes wrong
            return make_response({'message': 'post messages went wrong'}, 422)
        return make_response(new_message.to_dict(), 201)
        
api.add_resource(AllMessages, '/messages')

class OneMessage(Resource):

    def get_helper(self, id):
        q = Message.query.filter_by(id=id).first()
        if(not q):
            return make_response({"message": f'message {id} not found'}, 404)
        return q 
    
    def patch(self, id):
        q =  self.get_helper(id)
        try: 
            data = request.get_json()
            # loop through data
            # for each key, update q's key 
            for cur_field in data: 
                setattr(q, cur_field, data.get(cur_field))
            db.session.add(q)
            db.session.commit()
        except: 
            return make_response({"something went wrong"}, 422)
        return make_response(q.to_dict(), 200)

    def delete(self, id):
        q = self.get_helper(id)
        db.session.delete(q)
        db.session.commit()
        return make_response({}, 204)

api.add_resource(OneMessage, '/messages/<int:id>')

if __name__ == '__main__':
    app.run(port=4000, debug=True)
