	
""" 
Kibworth Acenstry Project API
"""

import boto3
from flask import Flask, jsonify, request
from flask_cors import CORS
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

app = Flask(__name__)
cors = CORS(app)
	
client = boto3.client('dynamodb')

TB_DETAILS='kibworth-villager-details'
TB_CENSUS='kibworth-villager-census'
TB_ER='kibworth-villager-er'
IND_SURNAME='SURNAME_SEARCH-index'
IND_ADDR='FIRST_ADD_SEARCH-index'
IND_FIRSTNAME_SURNAME='FIRSTNAME_SURNAME_SEARCH-index'
MAX_PAGE_SIZE=50

@app.route("/")
def root():
    """Get ancestor details by ID"""    
    return ok_response({'message': 'Welcome to the Kibworth Ancestry Public API'})

@app.route("/details/<string:uuid>")    
def getDetailsByUuid(uuid: str):
    """Get ancestor details by ID"""
    resp = client.get_item(
        TableName=TB_DETAILS,
        Key={
            'uuid': { 'S': uuid }
        }      
    )
    item = resp.get('Item')
    if not item:
        return error_response('No details found for ' + uuid, 404)
    return ok_response(dynamo_obj_to_python_obj(item))

@app.route("/detailsTop/<int:n>")
def topN(n: int):
    """Get top n results from details table"""
    if n > MAX_PAGE_SIZE:
        return error_response(f'Maximum supported page size = {MAX_PAGE_SIZE}', 400)
    resp = client.scan(TableName=TB_DETAILS, Limit=n)
    results = [ dynamo_obj_to_python_obj(r) for r in resp.get('Items') ]
    return ok_response(sortByUUID(results))
    
@app.route("/detailsBySurname/<string:surname>")    
def getDetailsBySurname(surname: str):
    """Get ancestor details by surname"""    
    resp = client.query(
        TableName=TB_DETAILS,
        IndexName=IND_SURNAME,
        ExpressionAttributeValues={
            ':v1': {
                'S': surname.upper(),
            },
        },
        KeyConditionExpression='SURNAME_SEARCH = :v1'       
    )
    items = resp.get('Items')
    if not items or len(items) < 1:
        return error_response('No details found for ' + surname, 404)
    results = [ dynamo_obj_to_python_obj(r) for r in items ]
    return ok_response(sortByUUID(results))  
    
@app.route("/detailsByFirstnameSurname/<string:firstnamesurname>")    
def getDetailsByFirstnameSurname(firstnamesurname: str):
    """Get ancestor details by surname"""    
    resp = client.query(
        TableName=TB_DETAILS,
        IndexName=IND_FIRSTNAME_SURNAME,
        ExpressionAttributeValues={
            ':v1': {
                'S': firstnamesurname.replace(" ","").upper(),
            },
        },
        KeyConditionExpression='FIRSTNAME_SURNAME_SEARCH = :v1'       
    )
    items = resp.get('Items')
    if not items or len(items) < 1:
        return error_response('No details found for ' + firstnamesurname, 404)
    results = [ dynamo_obj_to_python_obj(r) for r in items ]
    return ok_response(sortByUUID(results))      
    
@app.route("/detailsByAddr/<string:addr>")    
def getDetailsByAddr(addr: str):
    """Get ancestor details by Address (FIRST_ADD)"""    
    resp = client.query(
        TableName=TB_DETAILS,
        IndexName=IND_ADDR,
        ExpressionAttributeValues={
            ':v1': {
                'S': addr.upper(),
            },
        },
        KeyConditionExpression='FIRST_ADD_SEARCH = :v1'       
    )
    items = resp.get('Items')
    if not items or len(items) < 1:
        return error_response('No details found for ' + addr, 404)
    results = [ dynamo_obj_to_python_obj(r) for r in items ]
    return ok_response(sortByUUID(results))       

@app.route("/census/<string:uuid>")    
def getCensusByUuid(uuid: str):
    """Get ancestor census details by ID"""    
    resp = client.get_item(
        TableName=TB_CENSUS,
        Key={
            'uuid': { 'S': uuid }
        }      
    )
    item = resp.get('Item')
    if not item:
        return error_response('No census details found for ' + uuid, 404)
    return ok_response(dynamo_obj_to_python_obj(item))
    
@app.route("/er/<string:uuid>")    
def getERByUuid(uuid: str):
    """Get ancestor electoral register details by ID"""     
    resp = client.get_item(
        TableName=TB_ER,
        Key={
            'uuid': { 'S': uuid }
        }      
    )
    item = resp.get('Item')
    if not item:
        return error_response('No electoral register details found for ' + uuid, 404)
    return ok_response(dynamo_obj_to_python_obj(item))    

### HELPER FUNCTIONS ###

def dynamo_obj_to_python_obj(dynamo_obj: dict) -> dict:
    deserializer = TypeDeserializer()
    return {
        k: deserializer.deserialize(v) 
        for k, v in dynamo_obj.items()
    }  
  
def python_obj_to_dynamo_obj(python_obj: dict) -> dict:
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in python_obj.items()
    }

def ok_response(body) -> dict:
    return jsonify(body)
    
def error_response(message: str, error_code: int) -> dict:
    return jsonify({'error': message}), error_code
    
def sortByUUID(records):
    return sorted(records, key=lambda record: record.get('uuid'))