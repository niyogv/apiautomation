# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# import requests
# import json
# from faker import Faker
#
#
# # Read properties and payload files
# def read_from_file(filepath):
#     with open(filepath, 'r') as file:
#         return json.load(file)
#
# fake=Faker()
#
# ### For local
# property=read_from_file('properties.json')
# payload=read_from_file('../reports/payload.json')
# #
# #### For docker
# # property=read_from_file('/test/properties.json')
# # payload=read_from_file('/test/payload.json')
#
# payload['report']['create']['reportName']=fake.name()
#
# headers = {
#     "Authorization": property.get("report", {}).get("auth", ""),
#     "Content-Type": "application/json"
# }
#
#
# headers_without_token = {
#     "Authorization": property.get('report', {}).get('without_auth', ''),
#     "Content-Type": "application/json"
# }
#
# # MongoDB connection
# uri = "mongodb+srv://niyog:Test1234@cluster0.maawl0f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = MongoClient(uri, server_api=ServerApi('1'))
# db = client["test"]
# collection = db["testing"]
#
# # Test report class
# class Test_report():
#     report_id = None
#     report_duplicate_name = None
#
#     def test_create(self):
#         url = property['report']['create report']
#         data = payload['report']['create']
#         response = requests.post(url, headers=headers, json=data)
#         response_body = response.json()
#         Test_report.report_id = response_body['id']
#         Test_report.report_duplicate_name = response_body['name']
#         assert response.status_code == 200
#         assert response_body['name'] == payload['report']['create']['reportName']
#         struc = json.dumps(response_body, indent=4)
#         print(struc)
#
#         # Insert response into MongoDB
#         collection.insert_one(response_body)
#
#         # Retrieve the document from MongoDB
#         mongo_response = collection.find_one({"id": Test_report.report_id})
#         assert mongo_response is not None, "Document not found in MongoDB"
#         assert mongo_response['name'] == response_body['name'], "MongoDB document name does not match response body name"
#         print(mongo_response)