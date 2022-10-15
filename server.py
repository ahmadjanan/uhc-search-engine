from typing import Dict
from flask import Flask, render_template, request
import json

HOST_NAME = "localhost"
HOST_PORT = 80
DBFILE = "users.db"
app = Flask(__name__)


def get_ein_query_result(search: str) -> Dict:
    '''
    This function reads the JSON file and looks for the EIN search query in the EIN DB.

    Parameters
    ----------
    search: str
        Search term.

    Returns
    -------
    results: Dict
        Dictionary containing matching company data.
    '''

    with open('ein_db.json') as db:
        database = json.loads(db.read())
  
    results = database.get(search, {})

    if results:
        return {
            'name': results[0]['company_name'],
            'plans': results
        }

    return results


def get_name_query_result(search: str) -> Dict:
    '''
    This function reads the JSON file and looks for the company name search query in the Name DB.

    Parameters
    ----------
    search: str
        Search term.

    Returns
    -------
    results: Dict
        Dictionary containing matching company data.
    '''

    with open('name_db.json') as db:
        database = json.loads(db.read())

    results = database.get(search, {})
    if results:
        return {
          'name': search,
          'plans': results 
        }

    return results


def get_company_data(search: str) -> Dict:
    '''
    This function checks whether the query is EIN or Company name and searches in appropriate DB.

    Parameters
    ----------
    search: str
        Search term.

    Returns
    -------
    results: Dict
        Dictionary containing matching company data.
    '''

    if search.isnumeric():
        return get_ein_query_result(search)
    return get_name_query_result(search) 


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = dict(request.form)
        company_data = get_company_data(data["search"])
    else:
        company_data = {}

    return render_template("uhc-search.html", company_data=company_data)


if __name__ == "__main__":
    app.run(HOST_NAME, HOST_PORT)
