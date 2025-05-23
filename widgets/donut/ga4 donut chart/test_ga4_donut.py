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
payload=read_from_file('/test//donut/ga4 donut chart/payload.json')
payload['report']['create']['reportName']=fake.name()


class Test_donut():
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
        Test_donut.auth = "Bearer " + response_body['accessToken']
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_create_report(self):
        url=property['report']['create report']
        data=payload['report']['create']
        headers = {
            "Authorization": Test_donut.auth,
            "Content-Type": "application/json"
        }
        response=requests.post(url,headers=headers,json=data)
        response_body=response.json()
        Test_donut.report_id=response_body['id']
        Test_donut.report_name=response_body['name']
        assert response.status_code==200
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_create_standard_metrics(self):
        url=property['chart']['create chart']
        payload_donut_chart = payload['report']['donut'].copy()
        payload_donut_chart['reportId'] = Test_donut.report_id
        payload_donut_chart['title']=fake.name()
        data = payload_donut_chart
        headers = {
            "Authorization": Test_donut.auth,
            "Content-Type": "application/json"
        }
        response=requests.post(url,headers=headers,json=data)
        response_body=response.json()
        Test_donut.widget_body=response_body
        Test_donut.widget_title=response_body['title']
        Test_donut.widget_id=response_body['widgetId']
        assert response.status_code==200
        assert response_body['reportId']==Test_donut.report_id
        assert response_body['integrationType']=='GOOGLE_ANALYTICS_FOUR'
        assert response_body['startDate']=='2025-02-18T00:00:00.000+00:00'
        assert response_body['endDate']=='2025-03-19T23:59:59.999+00:00'
        assert response_body['dateRangeType']=='LAST_THIRTY_DAYS'
        assert response_body['recordType']=='GA4_ACCOUNT'
        assert response_body['title']==Test_donut.widget_title
        assert response_body['chartType']=='DONUT_CHART'
        assert response_body['chartWidth']==4
        assert response_body['chartHeight']==16
        response_body=response.json()
        struc=json.dumps(response_body, indent=4)
        print(struc)

    def test_download_csv(self):
        url = property['chart']['download csv']
        data = payload['download'].copy()
        data['widgetId'] = Test_donut.widget_id
        headers = {
            "Authorization": Test_donut.auth,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 200
        print(response.text)

    def test_task(self):
        url = property['chart']['task']
        data = payload['task'].copy()
        data['widgetId'] = Test_donut.widget_id
        headers = {
            "Authorization": Test_donut.auth,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 200

    def test_update_custom_metric(self):
        url = property['chart']['update chart']+Test_donut.widget_id+"/"+"widget-id"
        Test_donut.widget_body['title']=fake.name()
        Test_donut.widget_body['chartWidth']=10
        Test_donut.widget_body['chartHeight']=20
        Test_donut.widget_body['aggregation']='WEEKLY'
        Test_donut.widget_body['recordType']='GA4_ACCOUNT'
        Test_donut.widget_body['dateRangeType']='CUSTOM'
        Test_donut.widget_body['startDate']='2024-03-17T00:00:00.000+00:00'
        Test_donut.widget_body['endDate']='2025-03-17T23:59:59.999+00:00'
        Test_donut.widget_body['donutChart']['metric']['key'] = 'automation_backend_ga4_custom_metrics_C_1_C'
        Test_donut.widget_body['donutChart']['metric']['customMetric']=True
        headers = {
            "Authorization": Test_donut.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=Test_donut.widget_body)
        response_body = response.json()
        assert response.status_code == 200
        assert response_body['title']==Test_donut.widget_body['title']
        assert response_body['chartWidth']==Test_donut.widget_body['chartWidth']
        assert response_body['chartHeight']==Test_donut.widget_body['chartHeight']
        assert response_body['excludeWeekends']==Test_donut.widget_body['excludeWeekends']
        assert response_body['aggregation']==Test_donut.widget_body['aggregation']
        assert response_body['dateRangeType']==Test_donut.widget_body['dateRangeType']
        assert response_body['startDate']==Test_donut.widget_body['startDate']
        assert response_body['endDate']==Test_donut.widget_body['endDate']
        assert response_body['recordType']==Test_donut.widget_body['recordType']
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_get_widgets(self):
        url=property['chart']['get chart']+Test_donut.report_id+"/widgets"
        headers = {
            "Authorization": Test_donut.auth,
            "Content-Type": "application/json"
        }
        response=requests.get(url,headers=headers)
        response_body=response.json()
        assert response.status_code==200
        assert response_body['reportName']==Test_donut.report_name
        assert response_body['viewType']=='PRIVATE'
        assert response_body['widgets'][0]['reportId']==Test_donut.report_id
        assert response_body['widgets'][0]['integrationType']=='GOOGLE_ANALYTICS_FOUR'
        assert response_body['widgets'][0]['chartType']=='DONUT_CHART'
        assert response_body['widgets'][0]['startDate']=='2024-03-17T00:00:00.000+00:00'
        assert response_body['widgets'][0]['endDate']=='2025-03-17T23:59:59.999+00:00'
        assert response_body['widgets'][0]['dateRangeType']=='CUSTOM'
        assert response_body['widgets'][0]['aggregation']=='WEEKLY'
        assert response_body['widgets'][0]['recordType']=='GA4_ACCOUNT'
        assert response_body['widgets'][0]['excludeWeekends']==False
        assert response_body['widgets'][0]['chartWidth']==10
        assert response_body['widgets'][0]['chartHeight']==20
        stru=json.dumps(response_body,indent=4)
        print(stru)

    def test_custom_filter_add(self):
        url = property['chart']['create chart']+'/'+Test_donut.widget_id+"/"+"widget-id"
        payload_donut_chart = Test_donut.widget_body
        payload_donut_chart['widgetFilters'] = payload['report']['custom filter']
        data = payload_donut_chart
        headers = {
            "Authorization": Test_donut.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=data)
        assert response.status_code==200
        response_body = response.json()
        Test_donut.widget_body=response_body
        Test_donut.custom_filter_id=response_body['widgetFilters'][0]['id']
        assert response_body['widgetFilters'][0]['id'] == Test_donut.custom_filter_id
        assert response_body['widgetFilters'][0]['filterApplied'] == True
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_custom_filter_remove(self):
        url = property['chart']['create chart']+'/'+Test_donut.widget_id+"/"+"widget-id"
        payload_donut_chart = Test_donut.widget_body
        payload_donut_chart['widgetFilters'] = payload['report']['custom filter']
        payload_donut_chart['widgetFilters'][0]['filterApplied'] = False
        data = payload_donut_chart
        headers = {
            "Authorization": Test_donut.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=data)
        assert response.status_code==200
        response_body = response.json()
        Test_donut.widget_body=response_body
        Test_donut.custom_filter_id=response_body['widgetFilters'][0]['id']
        assert response_body['widgetFilters'][0]['id'] == Test_donut.custom_filter_id
        assert response_body['widgetFilters'][0]['filterApplied'] == False
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_global_filter_add(self):
        url = property['chart']['create chart']+'/'+Test_donut.widget_id+"/"+"widget-id"
        payload_donut_chart = Test_donut.widget_body
        payload_donut_chart['globalFiltersMap'] = payload['report']['global filter']['globalFiltersMap']
        payload_donut_chart['widgetFilters'] = payload['report']['global filter']['widget filter']['widgetFilters']
        data = payload_donut_chart
        headers = {
            "Authorization": Test_donut.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=data)
        assert response.status_code==200
        response_body = response.json()
        response_body['globalFiltersMap']= Test_donut.global_filter_id
        assert response_body['globalFiltersMap'] == Test_donut.global_filter_id
        assert response_body['widgetFilters'][0]['filterApplied'] == True
        struc = json.dumps(response_body, indent=4)
        print(struc)
        
    def test_summary(self):
        url = property['chart']['summary']
        data = payload['summary'].copy()
        data['widgetId'] = Test_donut.widget_id
        data['reportId'] = Test_donut.report_id
        headers = {
            "Authorization": Test_donut.auth,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 200

    def test_delete_widget(self):
        url = property['chart']['delete chart'] + Test_donut.report_id + "/report-id" + "/"+Test_donut.widget_id + "/widget-id"
        headers = {
            "Authorization": Test_donut.auth,
            "Content-Type": "application/json"
        }
        response = requests.delete(url, headers=headers)
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['message'] == 'Success'

    def test_delete_report(self):
        url = property['report']['delete report'] + Test_donut.report_id
        headers = {
            "Authorization": Test_donut.auth,
            "Content-Type": "application/json"
        }
        response = requests.delete(url, headers=headers)
        response_body = response.json()
        assert response_body['message'] == 'Success'
