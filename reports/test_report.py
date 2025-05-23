import pytest
import json
import requests
from faker import Faker

# Read properties and payload files
def read_from_file(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

fake=Faker()

### For local
# property=read_from_file('properties.json')
# payload=read_from_file('payload.json')
#
#### For docker
property=read_from_file('/test/properties.json')
payload=read_from_file('/test/payload.json')

payload['report']['create']['reportName']=fake.name()


headers_without_token = {
    "Authorization": property.get('report', {}).get('without_auth', ''),
    "Content-Type": "application/json"
}

class Test_report():
    report_id=None
    report_duplicate_name=None
    report_duplicate_id=None
    auth = None

    def write_payload_to_file(self):
        """Write updated payload back to file (optional and only when needed)."""
        with open('/reports/payload.json', 'w') as outfile:
            json.dump(payload, outfile, indent=4)

    def test_login(self):
        url = property['report']['login']
        data = payload['login']
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data)
        response_body = response.json()
        assert response.status_code == 200
        Test_report.auth = "Bearer " + response_body['accessToken']
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_create(self):
        url=property['report']['create report']
        data=payload['report']['create']
        headers = {
            "Authorization": Test_report.auth,
            "Content-Type": "application/json"
        }
        response=requests.post(url,headers=headers,json=data)
        response_body=response.json()
        Test_report.report_id=response_body['id']
        Test_report.report_duplicate_name=response_body['name']
        assert response.status_code==200
        assert response_body['name']==payload['report']['create']['reportName']
        struc=json.dumps(response_body,indent=4)
        print(struc)

    def test_share_view(self):
        url = property['report']['share access']
        payload_share_view=payload['report']['share access'].copy()
        payload_share_view['reportId'] = Test_report.report_id
        headers = {
            "Authorization": Test_report.auth,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=payload_share_view)
        response_body = response.json()
        struc=json.dumps(response_body,indent=4)
        print(struc)
        assert response.status_code==200
        assert response_body[0]['fullName']=='niyog.v'
        assert response_body[0]['accessType']=='VIEW'

    def test_share_edit(self):
        url = property['report']['share access']
        payload_share_edit=payload['report']['share access'].copy()
        payload_share_edit['reportId'] = Test_report.report_id
        payload_share_edit['userDetails'][0]['accessType'] = 'EDIT'
        headers = {
            "Authorization": Test_report.auth,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=payload_share_edit)
        response_body = response.json()
        struc=json.dumps(response_body,indent=4)
        print(struc)
        assert response.status_code==200
        assert response_body[0]['fullName']=='niyog.v'
        assert response_body[0]['accessType']=='EDIT'

    def test_share_comment(self):
        url = property['report']['share access']
        payload_share_comment=payload['report']['share access'].copy()
        payload_share_comment['reportId'] = Test_report.report_id
        payload_share_comment['userDetails'][0]['accessType'] = 'COMMENT'
        headers = {
            "Authorization": Test_report.auth,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=payload_share_comment)
        response_body = response.json()
        struc=json.dumps(response_body,indent=4)
        print(struc)
        assert response.status_code==200
        assert response_body[0]['fullName']=='niyog.v'
        assert response_body[0]['accessType']=='COMMENT'

    def test_create_same_name(self):
        url=property['report']['create report']
        data= {
            "reportName": Test_report.report_duplicate_name
        }
        headers = {
            "Authorization": Test_report.auth,
            "Content-Type": "application/json"
        }
        response=requests.post(url,headers=headers,json=data)
        response_body=response.json()
        assert response.status_code==412
        assert response_body['message']=='The report name already exists in your organization'
        struc=json.dumps(response_body,indent=4)
        print(struc)

    def test_create_without_name(self):
        url=property['report']['create report']
        data= payload['report']['create_without_name']
        headers = {
            "Authorization": Test_report.auth,
            "Content-Type": "application/json"
        }
        response=requests.post(url,headers=headers,json=data)
        response_body=response.json()
        assert response.status_code==400
        # assert response_body['message']=='The report name already exists in your organization'
        struc=json.dumps(response_body,indent=4)
        print(struc)

    def test_create_without_access_token(self):
        url=property['report']['create report']
        data=payload['report']['create']
        response=requests.post(url,headers=headers_without_token,json=data)
        response_body=response.json()
        assert response.status_code==401
        assert response_body["status"]=="UNAUTHORIZED"
        assert response_body['message']=="Access token is not valid or expired. Please generate a new access token"
        struc=json.dumps(response_body,indent=4)
        print(struc)


    def test_put(self):
        url=property['report']['update reports']+Test_report.report_id
        data=payload['report']['update']
        headers = {
            "Authorization": Test_report.auth,
            "Content-Type": "application/json"
        }
        response=requests.put(url,headers=headers,json=data)
        response_body=response.json()
        assert response.status_code==200
        assert response_body['name']=='check'
        struc=json.dumps(response_body, indent=4)
        print(struc)

    def test_duplicate(self):
        url=property['report']['duplicate report']+Test_report.report_id
        data=payload['report']['duplicate']
        headers = {
            "Authorization": Test_report.auth,
            "Content-Type": "application/json"
        }
        response=requests.post(url,headers=headers,json=data)
        response_body=response.json()
        Test_report.report_duplicate_id=response_body['id']
        assert response_body['message']=='Success'
        struc=json.dumps(response_body, indent=4)
        print(struc)

    def test_get(self):
        url=property['report']['view reports']
        headers = {
            "Authorization": Test_report.auth,
            "Content-Type": "application/json"
        }
        response=requests.get(url,headers=headers)
        response_body=response.json()
        assert any(item['name'] == 'check' for item in response_body['data']), "No element with name 'check' found"
        for item in response_body['data']:
            if item['name'] == 'checking':
                Test_report.report_duplicate = item['id']
                break
        struc=json.dumps(response_body, indent=4)
        print(struc)

    def test_delete(self):
        url=property['report']['delete report']+Test_report.report_id
        headers = {
            "Authorization": Test_report.auth,
            "Content-Type": "application/json"
        }
        response=requests.delete(url,headers=headers)
        response_body=response.json()
        assert response_body['message']=='Success'
        struc=json.dumps(response_body, indent=4)
        print(struc)

    def test_delete_duplicate(self):
        url=property['report']['delete report']+Test_report.report_duplicate_id
        headers = {
            "Authorization": Test_report.auth,
            "Content-Type": "application/json"
        }
        response=requests.delete(url,headers=headers)
        response_body=response.json()
        assert response_body['message'] == 'Success'
        struc = json.dumps(response_body, indent=4)
        print(struc)
