from flask import Flask
import data

app  = Flask(__name__)
data = data.PhoneDataLayer()

def get_results(n=None):

    if n is not None:
        if not isinstance(n, int):
            return None

    entries = data.get_entries(n)
    if entries is None:
        return None

    return u'[' + u', '.join(map(unicode, entries)) + u']'

def get_results_by_area(area_code, n=None):

    if not isinstance(area_code, int) or len(str(area_code)) != 3:
        return None
    if n is not None:
        if not isinstance(n, int):
            return None
        if n<=0:
            return None

    entries = data.get_all_entries()
    if entries is None:
        return None
    
    d = filter(lambda entry: entry.area_code == str(area_code), entries)
    if n:
        return u'[' + u', '.join(map(unicode, d[:n])) + u']'
    else:
        return u'[' + u', '.join(map(unicode, d)) + u']'

@app.route('/interview/api/v1.0/results', methods=['GET'])
def results():
    #print('here')
    return get_results()

@app.route('/interview/api/v1.0/results/<int:number>', methods=['GET'])
def results_with_limit(number):
    return get_results(number)

@app.route('/interview/api/v1.0/resultsForArea/<string:area_code>', methods=['GET'])
def results_by_area(area_code):
    return get_results_by_area(area_code)

@app.route('/interview/api/v1.0/resultsForArea/<string:area_code>/<int:number>', methods=['GET'])
def results_by_area_with_limit(area_code, number):
    return get_results_by_area(area_code, number)

if __name__ == '__main__':
    app.run(debug=True)
