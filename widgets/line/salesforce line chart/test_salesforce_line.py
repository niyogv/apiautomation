import pytest
import json
import requests
from faker import Faker

# Read properties and payload files
def read_from_file(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

fake=Faker()

## For local
# property=read_from_file('../../properties.json')
# payload=read_from_file('payload.json')
# payload['report']['create']['reportName']=fake.name()
#
#### For docker
property=read_from_file('/test/properties.json')
payload=read_from_file('/test/line/salesforce line chart/payload.json')
payload['report']['create']['reportName']=fake.name()

class Test_line():
    report_id = None
    report_name=None
    widget_title=None
    widget_id=None
    widget_body=None
    custom_filter_id=None
    global_filter_id = None
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
        Test_line.auth = "Bearer " + response_body['accessToken']
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_create_report(self):
        url=property['report']['create report']
        data=payload['report']['create']
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response=requests.post(url,headers=headers,json=data)
        response_body=response.json()
        Test_line.report_id=response_body['id']
        Test_line.report_name=response_body['name']
        assert response.status_code==200
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_create_standard_metrics(self):
        url=property['chart']['create chart']
        payload_line_chart = payload['report']['line'].copy()
        payload_line_chart['reportId'] = Test_line.report_id
        payload_line_chart['title']=fake.name()
        data = payload_line_chart
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response=requests.post(url,headers=headers,json=data)
        response_body=response.json()
        Test_line.widget_body=response_body
        Test_line.widget_title=response_body['title']
        Test_line.widget_id=response_body['widgetId']
        assert response.status_code==200
        assert response_body['reportId']==Test_line.report_id
        assert response_body['integrationType']=='SALESFORCE_CRM'
        assert response_body["lineChartWithOneDropdown"]["xAxis"][0]["key"] == "lastActivityDate"
        assert response_body["lineChartWithOneDropdown"]["yAxis"][0]["key"] == "recordCount"
        assert response_body['startDate']=='2024-02-05T00:00:00.000+00:00'
        assert response_body['endDate']=='2025-02-03T23:59:59.999+00:00'
        assert response_body['dateRangeType']=='DAY_LAST_THREE_SIXTY_FIVE_DAYS'
        assert response_body['aggregation']=='QUARTERLY'
        assert response_body['recordType']=='SALESFORCE_CONTACT'
        assert response_body['excludeWeekends']==False
        assert response_body['title']==Test_line.widget_title
        assert response_body['chartType']=='LINE_CHART_WITH_ONE_DROPDOWN'
        assert response_body['chartWidth']==8
        assert response_body['chartHeight']==16
        response_body=response.json()
        struc=json.dumps(response_body, indent=4)
        print(struc)

    def test_download_csv(self):
        url = property['chart']['download csv']
        data = payload['download'].copy()
        data['widgetId'] = Test_line.widget_id
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 200
        print(response.text)

    def test_task(self):
        url = property['chart']['task']
        data = payload['task'].copy()
        data['widgetId'] = Test_line.widget_id
        data['integrationType'] = 'GOOGLE_ANALYTICS_FOUR'
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 200

    def test_custom_filter_add(self):
        url = property['chart']['create chart']+'/'+Test_line.widget_id+"/"+"widget-id"
        payload_line_chart = Test_line.widget_body
        payload_line_chart['widgetFilters'] = payload['report']['custom filter']
        data = payload_line_chart
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=data)
        assert response.status_code==200
        response_body = response.json()
        Test_line.widget_body=response_body
        Test_line.custom_filter_id=response_body['widgetFilters'][0]['id']
        assert response_body['widgetFilters'][0]['id'] == Test_line.custom_filter_id
        assert response_body['widgetFilters'][0]['filterApplied'] == True
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_custom_filter_remove(self):
        url = property['chart']['create chart']+'/'+Test_line.widget_id+"/"+"widget-id"
        payload_line_chart = Test_line.widget_body
        payload_line_chart['widgetFilters'] = payload['report']['custom filter']
        payload_line_chart['widgetFilters'][0]['filterApplied'] = False
        data = payload_line_chart
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=data)
        assert response.status_code==200
        response_body = response.json()
        Test_line.widget_body=response_body
        Test_line.custom_filter_id=response_body['widgetFilters'][0]['id']
        assert response_body['widgetFilters'][0]['id'] == Test_line.custom_filter_id
        assert response_body['widgetFilters'][0]['filterApplied'] == False
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_global_filter_add(self):
        url = property['chart']['create chart'] + '/' + Test_line.widget_id + "/" + "widget-id"
        payload_line_chart = Test_line.widget_body
        payload_line_chart['globalFiltersMap'] = payload['report']['global filter']['globalFiltersMap']
        payload_line_chart['widgetFilters'] = payload['report']['global filter']['widget filter']
        data = payload_line_chart
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=data)
        assert response.status_code == 200
        response_body = response.json()
        response_body['globalFiltersMap'] = Test_line.global_filter_id
        assert response_body['globalFiltersMap'] == Test_line.global_filter_id
        assert response_body['widgetFilters'][0]['filterApplied'] == True
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_get_widgets(self):
        url=property['chart']['get chart']+Test_line.report_id+"/widgets"
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response=requests.get(url,headers=headers)
        response_body=response.json()
        assert response.status_code==200
        assert response_body['reportName']==Test_line.report_name
        assert response_body['viewType']=='PRIVATE'
        assert response_body['widgets'][0]['reportId']==Test_line.report_id
        assert response_body['widgets'][0]['integrationType']=='SALESFORCE_CRM'
        assert response_body['widgets'][0]['chartType']=='LINE_CHART_WITH_ONE_DROPDOWN'
        assert response_body['widgets'][0]['startDate']=='2024-02-05T00:00:00.000+00:00'
        assert response_body['widgets'][0]['endDate']=='2025-02-03T23:59:59.999+00:00'
        assert response_body['widgets'][0]['dateRangeType']=='DAY_LAST_THREE_SIXTY_FIVE_DAYS'
        assert response_body['widgets'][0]['aggregation']=='QUARTERLY'
        assert response_body['widgets'][0]['recordType']=='SALESFORCE_CONTACT'
        assert response_body['widgets'][0]['title']==Test_line.widget_title
        assert response_body['widgets'][0]['excludeWeekends']==False
        assert response_body['widgets'][0]['chartWidth']==8
        assert response_body['widgets'][0]['chartHeight']==16
        stru=json.dumps(response_body,indent=4)
        print(stru)

    def test_update_custom_metric(self):
        url = property['chart']['update chart']+Test_line.widget_id+"/"+"widget-id"
        Test_line.widget_body['title']=fake.name()
        Test_line.widget_body['chartWidth']=10
        Test_line.widget_body['chartHeight']=20
        Test_line.widget_body['excludeWeekends']=True
        Test_line.widget_body['aggregation']='MONTHLY'
        Test_line.widget_body['recordType']='SALESFORCE_LEAD'
        Test_line.widget_body['dateRangeType']='CUSTOM'
        Test_line.widget_body['startDate']='2022-03-17T00:00:00.000+00:00'
        Test_line.widget_body['endDate']='2024-03-17T23:59:59.999+00:00'
        Test_line.widget_body['lineChartWithOneDropdown']['xAxis'][0]['key']='leadConvertedDate'
        Test_line.widget_body['lineChartWithOneDropdown']['yAxis'][0]['key']='automation_sales_custom_metrics_check_C_1_C'
        Test_line.widget_body['lineChartWithOneDropdown']['yAxis'][0]['customMetric']=True
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=Test_line.widget_body)
        response_body = response.json()
        assert response.status_code == 200
        assert response_body['title']==Test_line.widget_body['title']
        assert response_body['chartWidth']==Test_line.widget_body['chartWidth']
        assert response_body['chartHeight']==Test_line.widget_body['chartHeight']
        assert response_body['excludeWeekends']==Test_line.widget_body['excludeWeekends']
        assert response_body['aggregation']==Test_line.widget_body['aggregation']
        assert response_body['dateRangeType']==Test_line.widget_body['dateRangeType']
        assert response_body['startDate']==Test_line.widget_body['startDate']
        assert response_body['endDate']==Test_line.widget_body['endDate']
        assert response_body['lineChartWithOneDropdown']['xAxis'][0]['key']==Test_line.widget_body['lineChartWithOneDropdown']['xAxis'][0]['key']
        assert response_body['lineChartWithOneDropdown']['yAxis'][0]['key']==Test_line.widget_body['lineChartWithOneDropdown']['yAxis'][0]['key']
        assert response_body['lineChartWithOneDropdown']['yAxis'][0]['customMetric']==True
        assert response_body['recordType']==Test_line.widget_body['recordType']
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_update_custom_dimension(self):
        url = property['chart']['update chart']+Test_line.widget_id+"/"+"widget-id"
        Test_line.widget_body['title']=fake.name()
        Test_line.widget_body['chartWidth']=10
        Test_line.widget_body['chartHeight']=20
        Test_line.widget_body['excludeWeekends']=True
        Test_line.widget_body['aggregation']='WEEKLY'
        Test_line.widget_body['recordType']='SALESFORCE_LEAD'
        Test_line.widget_body['dateRangeType']='CUSTOM'
        Test_line.widget_body['startDate']='2022-03-17T00:00:00.000+00:00'
        Test_line.widget_body['endDate']='2024-03-17T23:59:59.999+00:00'
        Test_line.widget_body['lineChartWithOneDropdown']['xAxis'][0]['key']='leadConvertedDate'
        Test_line.widget_body['lineChartWithOneDropdown']['yAxis'][0]['key']='automation_backend_custom_dimension_C_1_C'
        Test_line.widget_body['lineChartWithOneDropdown']['yAxis'][0]['customMetric']=False
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=Test_line.widget_body)
        response_body = response.json()
        assert response.status_code == 200
        assert response_body['title']==Test_line.widget_body['title']
        assert response_body['chartWidth']==Test_line.widget_body['chartWidth']
        assert response_body['chartHeight']==Test_line.widget_body['chartHeight']
        assert response_body['excludeWeekends']==Test_line.widget_body['excludeWeekends']
        assert response_body['aggregation']==Test_line.widget_body['aggregation']
        assert response_body['dateRangeType']==Test_line.widget_body['dateRangeType']
        assert response_body['startDate']==Test_line.widget_body['startDate']
        assert response_body['endDate']==Test_line.widget_body['endDate']
        assert response_body['lineChartWithOneDropdown']['xAxis'][0]['key']==Test_line.widget_body['lineChartWithOneDropdown']['xAxis'][0]['key']
        assert response_body['lineChartWithOneDropdown']['yAxis'][0]['key']==Test_line.widget_body['lineChartWithOneDropdown']['yAxis'][0]['key']
        assert response_body['lineChartWithOneDropdown']['yAxis'][0]['customMetric']==False
        assert response_body['recordType']==Test_line.widget_body['recordType']
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_update_funnel_stage(self):
        url = property['chart']['update chart']+Test_line.widget_id+"/"+"widget-id"
        Test_line.widget_body['title']=fake.name()
        Test_line.widget_body['chartWidth']=10
        Test_line.widget_body['chartHeight']=20
        Test_line.widget_body['excludeWeekends']=True
        Test_line.widget_body['aggregation']='DAILY'
        Test_line.widget_body['recordType']='SALESFORCE_LEAD'
        Test_line.widget_body['dateRangeType']='CUSTOM'
        Test_line.widget_body['startDate']='2022-03-17T00:00:00.000+00:00'
        Test_line.widget_body['endDate']='2024-03-17T23:59:59.999+00:00'
        Test_line.widget_body['lineChartWithOneDropdown']['xAxis'][0]['key']='leadConvertedDate'
        Test_line.widget_body['lineChartWithOneDropdown']['yAxis'][0]['key']='automation_backend_funnel_stage_C_1_C'
        Test_line.widget_body['lineChartWithOneDropdown']['yAxis'][0]['customMetric']=False
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=Test_line.widget_body)
        response_body = response.json()
        assert response.status_code == 200
        assert response_body['title']==Test_line.widget_body['title']
        assert response_body['chartWidth']==Test_line.widget_body['chartWidth']
        assert response_body['chartHeight']==Test_line.widget_body['chartHeight']
        assert response_body['excludeWeekends']==Test_line.widget_body['excludeWeekends']
        assert response_body['aggregation']==Test_line.widget_body['aggregation']
        assert response_body['dateRangeType']==Test_line.widget_body['dateRangeType']
        assert response_body['startDate']==Test_line.widget_body['startDate']
        assert response_body['endDate']==Test_line.widget_body['endDate']
        assert response_body['lineChartWithOneDropdown']['xAxis'][0]['key']==Test_line.widget_body['lineChartWithOneDropdown']['xAxis'][0]['key']
        assert response_body['lineChartWithOneDropdown']['yAxis'][0]['key']==Test_line.widget_body['lineChartWithOneDropdown']['yAxis'][0]['key']
        assert response_body['lineChartWithOneDropdown']['yAxis'][0]['customMetric']==False
        assert response_body['recordType']==Test_line.widget_body['recordType']
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_update_funnel_metric(self):
        url = property['chart']['update chart']+Test_line.widget_id+"/"+"widget-id"
        Test_line.widget_body['title']=fake.name()
        Test_line.widget_body['chartWidth']=10
        Test_line.widget_body['chartHeight']=20
        Test_line.widget_body['excludeWeekends']=True
        Test_line.widget_body['aggregation']='YEARLY'
        Test_line.widget_body['recordType']='SALESFORCE_LEAD'
        Test_line.widget_body['dateRangeType']='CUSTOM'
        Test_line.widget_body['startDate']='2022-03-17T00:00:00.000+00:00'
        Test_line.widget_body['endDate']='2024-03-17T23:59:59.999+00:00'
        Test_line.widget_body['lineChartWithOneDropdown']['xAxis'][0]['key']='leadConvertedDate'
        Test_line.widget_body['lineChartWithOneDropdown']['yAxis'][0]['key']='automation_backend_funnel_metrics_C_1_C'
        Test_line.widget_body['lineChartWithOneDropdown']['yAxis'][0]['customMetric']=False
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=Test_line.widget_body)
        response_body = response.json()
        assert response.status_code == 200
        assert response_body['title']==Test_line.widget_body['title']
        assert response_body['chartWidth']==Test_line.widget_body['chartWidth']
        assert response_body['chartHeight']==Test_line.widget_body['chartHeight']
        assert response_body['excludeWeekends']==Test_line.widget_body['excludeWeekends']
        assert response_body['aggregation']==Test_line.widget_body['aggregation']
        assert response_body['dateRangeType']==Test_line.widget_body['dateRangeType']
        assert response_body['startDate']==Test_line.widget_body['startDate']
        assert response_body['endDate']==Test_line.widget_body['endDate']
        assert response_body['lineChartWithOneDropdown']['xAxis'][0]['key']==Test_line.widget_body['lineChartWithOneDropdown']['xAxis'][0]['key']
        assert response_body['lineChartWithOneDropdown']['yAxis'][0]['key']==Test_line.widget_body['lineChartWithOneDropdown']['yAxis'][0]['key']
        assert response_body['lineChartWithOneDropdown']['yAxis'][0]['customMetric']==False
        assert response_body['recordType']==Test_line.widget_body['recordType']
        struc = json.dumps(response_body, indent=4)
        print(struc)

    def test_update_global_date_range(self):
        url=property['chart']['global date']
        data=payload['global date'].copy()
        data['reportId'] = Test_line.report_id
        headers={
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response=requests.post(url,headers=headers,json=data)
        response_body=response.json()
        assert response.status_code==200
        assert response_body['globalStartDate']=='2022-03-17T00:00:00.000+00:00'
        assert response_body['globalEndDate']=='2024-03-17T23:59:59.999+00:00'
        assert response_body['globalDateRange']=='CUSTOM'

    def test_widget_expansion(self):
        url = property['chart']['widget expansion']
        data = payload['widget expansion'].copy()
        headers= {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 200
        response_body = response.json()
        print(response_body)
        assert response_body[0]['date']=='01-01-2022'
        assert response_body[0]['year'] == 2022
        assert response_body[0]['maxEmployees']==0
        assert response_body[2]['date'] == '01-01-2024'
        assert response_body[2]['year'] == 2024
        assert response_body[2]['maxEmployees'] == 0

    def test_summary(self):
        url = property['chart']['summary']
        data = payload['summary'].copy()
        data['widgetId'] = Test_line.widget_id
        data['reportId'] = Test_line.report_id
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 200

    def test_widget_alerts(self):
        url = property['chart']['alerts']
        payload_alert = payload['widget alerts'].copy()
        payload_alert['widgetId'] = Test_line.widget_id
        data = payload_alert
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data)
        response_body = response.json()
        Test_line.alert_id = response_body['id']
        assert response.status_code == 200

    def test_widget_alerts_update(self):
        url = property['chart']['alerts'] + '/' + Test_line.alert_id
        payload_alert = payload['widget alerts'].copy()
        payload_alert['widgetId'] = Test_line.widget_id
        payload_alert['conditions'][0]['bucketConditions'][0]['value'] = '6'
        data = payload_alert
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=data)
        assert response.status_code == 200

    def test_alert_delete(self):
        url = property['chart']['alerts'] + '/' + Test_line.alert_id
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.delete(url, headers=headers)
        assert response.status_code == 200

    def test_two_dropdown(self):
        url = property['chart']['create chart'] + '/' + Test_line.widget_id + "/widget-id"
        Test_line.widget_body['chartType'] = 'LINE_CHART_WITH_TWO_DROPDOWN'
        original_chart = Test_line.widget_body['lineChartWithOneDropdown']
        x_axis = original_chart.get('xAxis', []).copy()
        y_axis = original_chart.get('yAxis', []).copy()
        y_axis.append({
            "color": "#F98E26",
            "customFieldTrend": "POSITIVE",
            "customMetric": False,
            "dataType": "FLOAT",
            "defaultField": False,
            "displayName": "*Act-On Lead Score",
            "funnelMetric": False,
            "funnelStage": False,
            "integrationType": "SALESFORCE_CRM",
            "key": "leadSource",
            "objectType": "SALESFORCE_CONTACT",
            "objectTypeDisplayName": "Contact",
            "parentObject": "SALESFORCE_CONTACT",
            "prefix": "",
            "suffix": ""
        })
        Test_line.widget_body['lineChartWithTwoDropdown'] = {
            "xAxis": x_axis,
            "yAxis": y_axis
        }
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=Test_line.widget_body)
        response_body = response.json()
        assert response.status_code == 200
        print(json.dumps(response_body, indent=4))

    def test_delete_widget(self):
        url = property['chart']['delete chart'] + Test_line.report_id + "/report-id" + "/"+Test_line.widget_id + "/widget-id"
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.delete(url, headers=headers)
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['message'] == 'Success'

    def test_delete_report(self):
        url = property['report']['delete report'] + Test_line.report_id
        headers = {
            "Authorization": Test_line.auth,
            "Content-Type": "application/json"
        }
        response = requests.delete(url, headers=headers)
        response_body = response.json()
        assert response_body['message'] == 'Success'


