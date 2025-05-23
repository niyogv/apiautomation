#!/bin/sh

set -e  # Optional: Stop on first failure

EXIT_CODE=0

pytest "/test/line/salesforce line chart/test_salesforce_line.py" || EXIT_CODE=1
pytest "/test/line/ga4 line chart/test_ga4_line.py" || EXIT_CODE=1
pytest "/test/line/google ads line chart/test_google_line.py" || EXIT_CODE=1
pytest "/test/donut/ga4 donut chart/test_ga4_donut.py" || EXIT_CODE=1
pytest "/test/donut/salesforce/test_salesforce_donut.py" || EXIT_CODE=1
pytest "/test/donut/google ads/test_google_donut.py" || EXIT_CODE=1
pytest "/test/tab/salesforce/test_salesforce.py" || EXIT_CODE=1

exit $EXIT_CODE
