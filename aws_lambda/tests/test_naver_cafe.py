from unittest import TestCase
from aws_lambda.local.naver_cafe import divide_by_6_month


class Test(TestCase):
    def test_divide_by_6_month(self):
        for start_date, end_date in [["2023-01-31", "2024-08-30"], ["2021-02-01", "2024-08-30"],
                                     ["2024-08-01", "2024-08-30"]]:
            dates = divide_by_6_month(start_date, end_date)
            print(dates)

    def test_divide_by_6_month2(self):
        for start_date, end_date in [["2024-07-31", "2024-08-30"]]:
            dates = divide_by_6_month(start_date, end_date)
            print(dates)
