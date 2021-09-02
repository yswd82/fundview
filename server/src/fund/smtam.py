# -*- coding: utf-8 -*-
import plotly.offline as plo
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data.reader import *
import dataclasses


@dataclasses.dataclass
class ReportTemplate:
    """
    テンプレートファイル情報クラス
    """
    template_file = ""
    css_file = ""

    def __init__(self, isin_code: str):
        self.dr = DataReader(isin_code)


class SmtamTemplate(ReportTemplate):
    """
    SMTAM形式テンプレート
    """
    template_file = "smtam_template_1.html"
    css_file = "style.css"

    def __init__(self, isin_code: str):
        super().__init__(isin_code)

        self.fund_name = self.dr.fund.name
        self.fund_category = self.dr.fund.category
        self.base_price_note = [
            "※ データは、当初設定日から作成基準日までを表示しています。",
            "※ 基準価額（分配金再投資）は、分配金（税引前）を再投資したものとして計算しています。",
            "※ 基準価額は、信託報酬控除後です。",
        ]
        self.base_price_return_note = "※ ファンドの騰落率は、分配金（税引前）を再投資したものとして計算しています。"
        self.distribution_since_established = 40

    @property
    def html_basic_price_graph(self) -> str:
        """
        基準価額のグラフを生成する

        :param df:
        :return:
        """
        df = self.dr.basic_price

        # サブプロットグラフの初期化
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        ymin = 0
        basic_price_max = df["basic_price"].max()

        if basic_price_max < 16000:
            ytick = 2500
        else:
            ytick = 5000

        ymax = (basic_price_max // 5000 + 1) * 5000

        yticks = (df["basic_price"].max() // 2000 + 1) - (df["basic_price"].min() // 2000)

        y2max = (df["net_asset_amount"].max() // 100000 + 1) * 100000

        # 基準価額追加
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["basic_price"],
                mode="lines",
                line=dict(width=1.0, color="rgb(255, 0, 0)"),
                hoverinfo="x+y",
                name="基準価額（円）：左目盛",
            ),
            secondary_y=False,
        )

        # 純資産総額追加
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["net_asset_amount"],
                mode="lines",
                line=dict(width=0.0, color="rgb(153, 204, 255)"),
                stackgroup="one",
                hoverinfo="x+y",
                name="純資産総額（億円）：右目盛",
                fill="tozeroy",
                # color="rgb(153, 204, 255)",
            ),
            secondary_y=True,
        )

        # X軸設定
        fig.update_xaxes(
            showgrid=False,
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            showticklabels=True,
            tick0=df.index[0],
            dtick="M36",
            ticks="inside",
        )

        # Y軸設定
        fig.update_yaxes(
            showgrid=False,
            # gridcolor="black",
            showline=False,
            # linewidth=1,
            # linecolor="black",
            mirror=True,
            showticklabels=True,
            dtick=ytick,
        )

        # レイアウト設定
        fig.update_layout(
            margin_l=10,
            margin_r=10,
            margin_t=10,
            margin_b=10,
            width=480,
            height=300,
            yaxis_range=[ymin, ymax],
            yaxis_tickformat=">0,d",
            yaxis2=dict(dtick=100000, overlaying="y"),
            # yaxis2=dict(overlaying="y"),
            # yaxis2_range=[0, y2max],
            showlegend=True,
            legend=dict(yanchor="bottom", y=-0.45, xanchor="left", x=0.00),
            hovermode="x",
        )

        ret_str = plo.plot(fig, output_type="div", include_plotlyjs="cdn", config=dict(displayModeBar=False))
        return ret_str

    @property
    def html_nav_aum(self) -> str:
        df = self.dr.nav_aum
        df = df.rename(
            columns={
                "basic_price": "基準価額",
                "net_asset_amount": "純資産総額",
            }
        )

        df = df.T.rename(columns={0: "当月末"})
        df["前月末"] = None

        ret_str = df.to_html(index=True, justify="unset", border="0", na_rep="", classes="nav_aum table")
        return ret_str

    @property
    def html_pct_change_by_period(self) -> str:
        df = self.dr.pct_change_by_period
        df = df.rename(columns={"period": "", "fund": "ファンド", "category": "カテゴリー"})
        df["差"] = ""
        ret_str = df.to_html(index=False, justify="unset", border="0", na_rep="", classes="pct_change table")
        return ret_str

    @property
    def html_dividend(self) -> str:
        df = self.dr.dividend
        df["y"] = df["period"].apply(lambda x: x.year)
        df["m"] = df["period"].apply(lambda x: x.month)

        df["年"] = df["y"].apply(lambda x: str(x) + "年")
        df["月"] = df["m"].apply(lambda x: str(x) + "月")

        col = ["2020年", "2021年"]

        for c in col:
            df[c] = df[df["年"] == c]["dividend"].apply(lambda x: str(int(x.replace(".00円", ""))) + "円")

        df = df.sort_values(["y", "m"])
        df = df[["m"] + col]
        df = df.set_index("m").dropna(how='all').groupby(by="m").max()

        df = df.T

        df.columns = [str(c) + "月" for c in df.columns]
        df = df.apply(lambda x: x.replace(".", ""))

        ret_str = df.to_html(index=True, header=True, border="0", na_rep="", classes="dividend table")
        return ret_str

    def get_ranking(self) -> list:
        rank = RankingReader().ranking
        return [(i, n, f) for i, n, f in zip(rank["isin_code"], rank["name"], rank["flow"])]
