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
# property=read_from_file('../../properties.json')
# payload=read_from_file('payload.json')
# payload['report']['create']['reportName']=fake.name()
#
#### For docker
property=read_from_file('/test/properties.json')
payload=read_from_file('/test//tab/salesforce/payload.json')
payload['report']['create']['reportName']=fake.name()


class Test_tab():
    report_id = None
    report_name=None
    widget_title=None
    widget_id=None
    widget_body=None
    custom_filter_id=None
    global_filter_id=None
    auth=None

    def test_login(self):
        url = property['report']['login']
        data = payload['login']
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data)
        response_body = response.json()
        assert response.status_code == 200
        Test_tab.auth = "Bearer " + response_body['accessToken']
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_create_report(self):
        url=property['report']['create report']
        data=payload['report']['create']
        headers = {
            "Authorization": Test_tab.auth,
            "Content-Type": "application/json"
        }
        response=requests.post(url,headers=headers,json=data)
        response_body=response.json()
        Test_tab.report_id=response_body['id']
        Test_tab.report_name=response_body['name']
        assert response.status_code==200
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_create_standard_dimension(self):
        url = property['chart']['create chart']
        payload_tab_chart = payload['tab'].copy()
        payload_tab_chart['reportId'] = Test_tab.report_id
        payload_tab_chart['title'] = fake.name()
        data = payload_tab_chart
        headers = {
            "Authorization": Test_tab.auth,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data)
        response_body = response.json()
        Test_tab.widget_body = response_body
        Test_tab.widget_title = response_body['title']
        Test_tab.widget_id = response_body['widgetId']
        assert response.status_code == 200
        assert response_body['reportId'] == Test_tab.report_id
        assert response_body['integrationType'] == 'SALESFORCE_CRM'
        assert response_body['startDate'] == '2025-03-25T00:00:00.000+00:00'
        assert response_body['endDate'] == '2025-04-23T23:59:59.999+00:00'
        assert response_body['dateRangeType'] == 'LAST_THIRTY_DAYS'
        assert response_body['recordType'] == 'SALESFORCE_LEAD'
        assert response_body['excludeWeekends'] == False
        assert response_body['title'] == Test_tab.widget_title
        assert response_body['chartType'] == 'TABULAR_WITH_NO_DROPDOWN'
        assert response_body['chartWidth'] == 8
        assert response_body['chartHeight'] == 16
        response_body = response.json()
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_update_custom_metric(self):
        url = property['chart']['update chart'] + Test_tab.widget_id + "/" + "widget-id"
        Test_tab.widget_body['title'] = fake.name()
        Test_tab.widget_body['chartWidth'] = 10
        Test_tab.widget_body['chartHeight'] = 20
        Test_tab.widget_body['aggregation'] = 'WEEKLY'
        Test_tab.widget_body['recordType'] = 'SALESFORCE_LEAD'
        Test_tab.widget_body['dateRangeType'] = 'CUSTOM'
        Test_tab.widget_body['startDate'] = '2024-03-17T00:00:00.000+00:00'
        Test_tab.widget_body['endDate'] = '2025-03-17T23:59:59.999+00:00'
        Test_tab.widget_body['tabularWithNoDropdown']['metrics'][0]['key'] = 'automation_sales_custom_metrics_check_C_1_C'
        Test_tab.widget_body['tabularWithNoDropdown']['dimensions'][0]['customMetric'] = True
        headers = {
            "Authorization": Test_tab.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=Test_tab.widget_body)
        response_body = response.json()
        assert response.status_code == 200
        assert response_body['title'] == Test_tab.widget_body['title']
        assert response_body['chartWidth'] == Test_tab.widget_body['chartWidth']
        assert response_body['chartHeight'] == Test_tab.widget_body['chartHeight']
        assert response_body['excludeWeekends'] == Test_tab.widget_body['excludeWeekends']
        assert response_body['aggregation'] == Test_tab.widget_body['aggregation']
        assert response_body['dateRangeType'] == Test_tab.widget_body['dateRangeType']
        assert response_body['startDate'] == Test_tab.widget_body['startDate']
        assert response_body['endDate'] == Test_tab.widget_body['endDate']
        assert response_body['recordType'] == Test_tab.widget_body['recordType']
        assert response_body['tabularWithNoDropdown']['metrics'][0]['key'] == Test_tab.widget_body['tabularWithNoDropdown']['metrics'][0]['key']
        struc = json.dumps(response_body, indent=4)
        print(struc)
        
    def test_task(self):
        url = property['chart']['task']
        data = payload['task'].copy()
        data['widgetId'] = Test_tab.widget_id
        headers = {
            "Authorization": Test_tab.auth,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 200
        
    def test_delete_widget(self):
        url = property['chart']['delete chart'] + Test_tab.report_id + "/report-id" + "/"+Test_tab.widget_id + "/widget-id"
        headers = {
            "Authorization": Test_tab.auth,
            "Content-Type": "application/json"
        }
        response = requests.delete(url, headers=headers)
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['message'] == 'Success'

    def test_delete_report(self):
        url = property['report']['delete report'] + Test_tab.report_id
        headers = {
            "Authorization": Test_tab.auth,
            "Content-Type": "application/json"
        }
        response = requests.delete(url, headers=headers)
        response_body = response.json()
        assert response_body['message'] == 'Success'

