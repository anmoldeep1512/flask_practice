# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from itertools import groupby
from operator import itemgetter

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:123@localhost:54320/dna_practice'
app.debug = True
db = SQLAlchemy(app)

""" create a table first, using the follwing commands :
    in terminal: 
    $ python
then
    >>>from app import app, db
    >>>app.app_context().push()
    >>>db.create_all()
"""

"""
    we'll have the data with positive and negative sentiment in similar way, 
    just a new column with these names can be added. 
"""


class ResponseData(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer(), primary_key=True)
    user_email = db.Column(db.String(), nullable=False)
    text = db.Column(db.String(), nullable=False)
    band = db.Column(db.String(), nullable=False)
    capability = db.Column(db.String(), nullable=False)

    def __init__(self, id, user_email, text, band, capability):
        self.id = id
        self.user_email = user_email
        self.text = text
        self.band = band
        self.capability = capability

@app.route("/responses", methods=["GET"])
def get_responses():
    all_responses = ResponseData.query.all()
    output = []
    for response in all_responses:
        curr_response = {"id": response.id, "user_email": response.user_email, "text": response.text,
                         "band": response.band, "capability": response.capability}
        output.append(curr_response)
    return jsonify(output)


def normalize_query(params):
    """
    Converts query parameters from only containing one value for each parameter,
    to include parameters with multiple values as lists.

    :param params: a flask query parameters data structure
    :return: a dict of normalized query parameters
    """
    params_non_flat = params.to_dict(flat=False)
    return {k: v for k, v in params_non_flat.items()}


# manipulate the response query to a dictionary
def convert_to_dict(res):
    output = []
    for response in res:
        curr_response = {"id": response.id, "user_email": response.user_email, "text": response.text,
                         "band": response.band, "capability": response.capability}
        output.append(curr_response)
    return output


# manipulate the output according to the desired json for frontend
def group_by_filter(output, filter_):
    final_res = {}
    for key, value in groupby(output,
                              key=itemgetter(filter_)):
        final_res[key] = []
        for k in value:
            final_res[key].append(k)
    return final_res

# get request in postman: "http://localhost:2020/filter_" 
@app.route("/filter_", methods=["GET"])
def particular_response():
    # as the request can have multiple variables to a single query parameter, so adding them as a list
    query_params = normalize_query(request.args)
    print(query_params)
    output = []
    final_res = {}

    # in case only band filter_ is applied
    if "band" in query_params and "capability" not in query_params:
        res = ResponseData.query.filter(ResponseData.band.in_(query_params["band"]))
        output = convert_to_dict(res)
        final_res = group_by_filter(output, 'band')

    # in case only capability filter_ is applied
    elif "capability" in query_params and "band" not in query_params:
        res = ResponseData.query.filter(ResponseData.capability.in_(query_params["capability"]))
        output = convert_to_dict(res)
        final_res = group_by_filter(output, 'capability')

    # in case both band and capability is chosen
    elif query_params["band"] and query_params["capability"]:
        print("in and")
        res = ResponseData.query.filter(
            ResponseData.band.in_(query_params["band"]) & ResponseData.capability.in_(query_params["capability"]))
        output = convert_to_dict(res)
        final_res = group_by_filter(output, 'capability')

    return jsonify(final_res)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host="localhost", port=2020, debug=True)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
