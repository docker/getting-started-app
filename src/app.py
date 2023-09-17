from flask import Flask, request
import os

from occurrence_counter import OccurrenceCounter

occurrence_counter = OccurrenceCounter()
app = Flask(__name__)

DEFAULT_FILE = 'data.txt'

@app.route('/occurrence_counter/file', methods=['POST'], endpoint='count_occurrences_in_file')
def count_occurrences_in_file():
    file = request.files.get('file')
    if file:
        try:
            occurrences = occurrence_counter.get_occurrences_from_file(file)
            return {'occurrences': occurrences}
        except Exception as e:
            return {'error': str(e)}, 500        

@app.route('/occurrence_counter', methods=['GET'], endpoint="count_occurrences_in_default")
def count_occurrences_in_default():
    n = int(request.args.get('n', -1))
    try:
        with open(DEFAULT_FILE, 'rb') as file:
            occurrences = occurrence_counter.get_occurrences_from_file(file, n)
            return {'occurrences': occurrences}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/occurrence_counter/wiki', methods=['GET'], endpoint="count_occurrences_wiki")
def count_occurrences_wiki():
    url = request.args.get('url')
    n = int(request.args.get('n', -1))
    try:
        if url is None:
            return {'error': 'url parameter is required'}, 400
        occurrences = occurrence_counter.get_occurrences_from_wiki_page(url, n)
        return {'occurrences': occurrences}
    except Exception as e:
        return {'error': str(e)}, 500
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

        
        