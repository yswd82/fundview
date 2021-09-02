# -*- coding: utf-8 -*-
from ToushinReader.core import Fund, Ranking
import pandas as pd
from datetime import datetime


class DataReader:
    def __init__(self, isin_code: str):
        self.fund = Fund(isin_code)

    @property
    def basic_price(self) -> pd.DataFrame:
        url = self.fund.historical_data_url

        # 日付形式のパース
        f = '%Y年%m月%d日'
        df = pd.read_csv(url, encoding="shift-jis", parse_dates=[0], date_parser=lambda x: datetime.strptime(x, f))

        df = df.rename(
            columns={
                "年月日": "date",
                "基準価額(円)": "basic_price",
                "純資産総額（百万円）": "net_asset_amount",
                "分配金": "dividend",
                "決算期": "closing_period",
            }
        )
        df = df.set_index("date")
        return df

    @property
    def nav_aum(self) -> pd.DataFrame:
        df = pd.DataFrame(
            {
                "basic_price": [self.fund.basic_price + "円"],
                "net_asset_amount": [self.fund.net_asset_amount]
            }
        )
        return df

    @property
    def pct_change_by_period(self) -> pd.DataFrame:
        df = pd.DataFrame(self.fund.pct_change)
        return df

    @property
    def dividend(self) -> pd.DataFrame:
        df = pd.DataFrame(self.fund.dividend)
        df = df.rename(
            columns={
                "date": "period",
                "amount": "dividend"
            }
        )
        df["period"] = pd.to_datetime(df["period"])
        return df


class RankingReader:
    def __init__(self):
        pass

    @property
    def ranking(self) -> dict:
        myrank = Ranking()
        return myrank.money_in_out



# if __name__ == '__main__':
#     isin_code = "JP90C0003PR7"
#     dr = DataReader(isin_code)
#     print(dr.basic_price)
