# -*- coding:utf-8 -*-
from flask import Flask, render_template
import os
from fund.smtam import *
import inspect
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__, static_folder='static', template_folder='templates')

env = Environment(
    loader=FileSystemLoader(
        "./templates/",
        encoding="utf8",
    )
)


@app.route("/")
def root():
    return render_template("index.html")


@app.route("/isin/<isin_code>")
def root_isin(isin_code: str):
    # /isin/配下にアクセスが有った場合はSmtamTemplateを使用する
    rep = SmtamTemplate(isin_code)
    params = inspect.getmembers(rep)

    return render_template(rep.template_file, **dict(params))


@app.route("/design_b/<isin_code>")
def root_bulma(isin_code: str):
    # /design_b/配下にアクセスがあった場合はtemplate_2を使う
    rep = SmtamTemplate(isin_code)
    rep.template_file = 'smtam_template_2.html'
    params = inspect.getmembers(rep)

    return render_template(rep.template_file, **dict(params))


if __name__ == "__main__":
    # サーバ起動用
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
