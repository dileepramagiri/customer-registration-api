from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
import re
import pandas as pd
from uuid import uuid4

app = Flask(__name__)
api = Api(app)

file_name = 'customers_table.xlsx'
customer_table = pd.read_excel(file_name)

def phone_number_validation(number):  
    if (str(number).isnumeric() != True) or (len(str(number)) != 10):
        raise ValueError('Phone number should contain 10 digits')
    return number

def email_validation(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError('Invalid Email id')
    return email
    
parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('phone_number', type=phone_number_validation, required=True, location='json')
parser.add_argument('email', type=email_validation, required=True, location='json')

resource_fields = {
    'message': fields.String,
    'customer_id':fields.String}
class RegistrationResource(Resource):
    @marshal_with(resource_fields)
    def post(self):
        input_data = parser.parse_args()
        phone_number = str(input_data['phone_number']).strip()
        email = str(input_data['email']).strip()
        
        # between(35 to 52 lines) I used pandas logic, But in real world we can use database ORM logic to do database CRUD operations using SQLAlchemy/Database client.
        for i in range(len(customer_table)):
            if (str(customer_table.loc[i,'phone_number']).strip() == phone_number) and (str(customer_table.loc[i,'email']).strip() == email):
                response = {
                    "message": "Customer already existed",
                    "customer_id": str(customer_table.loc[i,'customer_id']).strip()
                    }
                return response, 200
            elif str(customer_table.loc[i,'phone_number']).strip() == phone_number:
                abort(409, message='Phone number already existed')
                break
            elif str(customer_table.loc[i,'email']).strip() == email:
                abort(409, message='Email already existed')
                break
        else:
            customer_id = str(uuid4())
            customer_table.loc[len(customer_table)] = {'customer_id':customer_id, 'phone_number':phone_number, 'email':email}
            customer_table.to_excel(file_name, index=False)
            response = {'message':'New customer added successfully','customer_id': customer_id}
            return response, 201

api.add_resource(RegistrationResource, '/register', endpoint='registration_resource')

if __name__ == "__main__":
    app.run()
        