# -*- coding:utf-8 -*-
from jinja2 import Environment, FileSystemLoader
from fund.smtam import *
import inspect

env = Environment(
    loader=FileSystemLoader(
        "./templates/",
        encoding="utf8",
    )
)


def create_report(isin_code: str):
    """
    レポート定義ファイルを受け取ってテンプレートに展開する
    """
    rep = SmtamTemplate(isin_code)

    tmpl = env.get_template(rep.template_file)

    params = inspect.getmembers(rep)
    html = tmpl.render(**dict(params))
    return html


if __name__ == "__main__":
    # 定義クラス取得
    isin_code = "JP90C000H1T1"
    isin_code = "JP90C0003PR7"
    # isin_code = "JP90C0001530"

    # レポート生成
    create_report(isin_code)
