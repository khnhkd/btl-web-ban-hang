from flask import Flask
from flask_restful import Api
from modules.camera.camera import CameraWithoutId, CameraBrandWithoutId, CameraWithBrandId
from modules.laptop.laptop import LaptopWithoutId, LaptopBrandWithoutId
from modules.user.user import UserApi
from libraries.connect_database import connect_database, Camera, User, Laptop
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS

session = connect_database()

app = Flask(__name__)

cors = CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'

app.config['SECRET_KEY'] = 'khanhkd'

admin = Admin(app)
admin.add_view(ModelView(Camera, session()))
admin.add_view(ModelView(Laptop, session()))
admin.add_view(ModelView(User, session()))

api = Api(app)
api.add_resource(CameraWithoutId, '/camera', methods=['GET'])
api.add_resource(CameraWithBrandId, '/camera/<int:brand_id>', methods=['GET'])
api.add_resource(CameraBrandWithoutId, '/camera_brand', methods=['GET'])

api.add_resource(LaptopWithoutId, '/laptop', methods=['GET'])
api.add_resource(LaptopBrandWithoutId, '/laptop_brand', methods=['GET'])

api.add_resource(UserApi, '/user', methods=['POST'])

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', debug=True)
    except Exception as exp:
        print(exp)
