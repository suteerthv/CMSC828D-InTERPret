import json
import db_access
from flask import Flask, Response, render_template
import datetime
from functools import lru_cache

app = Flask(__name__, static_url_path='/static')

nonce = db_access.get_connection(debug=False)


@app.route('/', methods=["GET"])
def renderPage():
    return render_template("dashboard.html")


@app.route('/basic.js', methods=["GET"])
def renderVis():
    return render_template("basic.js")


@app.route('/get-date-range/<start_date>/<end_date>')
def get_date_range(start_date, end_date):
    # data = db_access.real_get_range_query(nonce, start_date, end_date)
    data = db_access.real_get_month_bin(nonce, start_date, end_date)

    resp = Response(response=json.dumps(data),
                    status=200, mimetype='application/json')
    h = resp.headers  # response to give back to user on browser
    h['Access-Control-Allow-Origin'] = "*"
    return resp  # send response to client

@app.route('/test/')
def lol_no_name():
    return "No Name"

@app.route('/test/<name>')
def lol(name):
    return name

@app.route('/get-data/<identity>')
@lru_cache(maxsize=10000)
def getData(identity):
    data = db_access.real_get_data_query(nonce, identity)

    resp = Response(response=json.dumps(data),
                    status=200,
                    mimetype='application/json')
    h = resp.headers  # response to give back to user on browser
    h['Access-Control-Allow-Origin'] = "*"
    return resp  # send response to client


@app.route('/get-paper-data/<s_dt>/<e_dt>/<keyword>')
@lru_cache(maxsize=10000)
def getPaperDataKey(s_dt, e_dt, keyword):
    start_dt = datetime.date.fromisoformat(s_dt)
    end_dt = datetime.date.fromisoformat(e_dt)

    data = db_access.get_paper_from_range(nonce, start_dt, end_dt, keyword)
    ret = {}
    for row in data:
        paper_id, paper_name, art_ids, dt, title, cat = row
        if paper_name not in ret:
            ret[paper_name] = [{paper_name: []}]

        dt = dt.isoformat()
        ts = datetime.time.fromisoformat("09:00:00-05:00")
        te = datetime.time.fromisoformat("21:00:00-05:00")
        curr = {"label": paper_name,
                "timeRange": ("%sT%s" % (dt, ts),
                              "%sT%s" % (dt, te)),
                "paper_id": paper_id,
                "paper_name": paper_name,
                "val": "No Keywords" if not cat else keyword,
                "article_ids": art_ids.split(", "),
                "title": title
                }
        ret[paper_name][0][paper_name].append(curr)

    out = []
    for k in ret:
        label = ret[k][0]
        for l_k in ret[k][0]:
            ret[k][0] = {"label": l_k, "data": label[k]}
        out.append({"group": k, "data": [ret[k][0]]})

    resp = Response(response=json.dumps(out), status=200,
                    mimetype='application/json')
    h = resp.headers  # response to give back to user on browser
    h['Access-Control-Allow-Origin'] = "*"
    return resp  # send response to client


@app.route('/get-paper-data/<s_dt>/<e_dt>')
@lru_cache(maxsize=10000)
def getPaperData(s_dt, e_dt):
    start_dt = datetime.date.fromisoformat(s_dt)
    end_dt = datetime.date.fromisoformat(e_dt)

    data = db_access.get_paper_from_range(nonce, start_dt, end_dt)

    # This converts the
    # {paper_name -> [{date, p_id, paper_name, a_id}]
    # ==> [{group: paper_name, "data": [{date, p_id, paper_name, a_id}]}]
    ret = {}
    for row in data:
        paper_id, paper_name, art_ids, dt, title, keywords = row
        print(paper_name, keywords)
        if paper_name not in ret:
            ret[paper_name] = [{paper_name: []}]

        dt = dt.isoformat()
        ts = datetime.time.fromisoformat("09:00:00-05:00")
        te = datetime.time.fromisoformat("21:00:00-05:00")
        curr = {"label": paper_name,
                "timeRange": ("%sT%s" % (dt, ts),
                              "%sT%s" % (dt, te)),
                "paper_id": paper_id,
                "paper_name": paper_name,
                "val": "No Keywords" if not keywords else keywords,
                "article_ids": art_ids.split(", "),
                "title": title
                }
        ret[paper_name][0][paper_name].append(curr)

    out = []
    for k in ret:
        label = ret[k][0]
        for l_k in ret[k][0]:
            ret[k][0] = {"label": l_k, "data": label[k]}
        out.append({"group": k, "data": [ret[k][0]]})

    resp = Response(response=json.dumps(out), status=200,
                    mimetype='application/json')
    h = resp.headers  # response to give back to user on browser
    h['Access-Control-Allow-Origin'] = "*"
    return resp  # send response to client


if __name__ == "__main__":
    app.run("127.0.0.1", debug=True, port=8000)
