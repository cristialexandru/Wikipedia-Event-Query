from flask import Flask, request
import pymongo
import json
app = Flask(__name__)

DB_TRANSLATE = {'events' : 'evs',
				'births' : 'brts',
				'deaths' : 'dths',
				'holidays' : 'holo'}

SERVER_ADDR = "localhost"

SERVER_PORT = 27017

@app.route('/')
def process_request():

	# Parse the request arguments
	year = request.args.get('year')
	day = request.args.get('day').lower()
	category = request.args.get('category')

	# Connect to the database and select the appropriate db
	client = pymongo.MongoClient(SERVER_ADDR, SERVER_PORT)
	database = client[DB_TRANSLATE[category.lower()]]
	collection = database[str(day)]
	result = []

	# Treat holidays differently
	if category != 'holidays':

		# Query the database
		for entry in collection.find({'year' : str(year)}):
			data = {}
			data['title'] = entry['desc']
			data['year'] = entry['year']
			data['day'] = entry['day']
			data['category'] = category
			result.append(data)
	else:
		for entry in collection.find():
			data = {}
			data['title'] = entry['desc']
			data['day'] = entry['day']
			data['category'] = category
			result.append(data)

	# Return the final result as JSON
	final_result = {}
	final_result['results'] = result
	json_result = json.dumps(final_result)
	return json_result


if __name__ == '__main__':
    app.run()