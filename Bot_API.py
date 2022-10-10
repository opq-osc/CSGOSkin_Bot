from flask import Flask, render_template, request

import Func

func = Func.CSGO()
app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    print(request.headers.get("User-Agent"))
    return render_template("./index.html", flag=1)


@app.route("/<string:short_code>", methods=["GET"])
def deal_url(short_code):
    QQ = func.Chk_API(short_code)
    if QQ:
        return render_template("./list.html", Code=short_code, QQ=QQ)
    else:
        return render_template("./index.html", flag=0)


@app.route("/db/<string:short_code>", methods=["GET"])
def get_data(short_code):
    return func.Get_data(short_code)


if __name__ == "__main__":
    app.run(debug=False, port=7355, threaded=True)
