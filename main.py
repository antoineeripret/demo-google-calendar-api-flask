#Import Flask
from flask import Flask, render_template, request
#Import main function from the other .py file 
from get_events import get_list_of_events

#Initialize app 
app = Flask(__name__)

#Create the / page 
@app.route('/',methods=["GET"])
def index():
	return render_template('index.html')

#Create the result if the user clicks on SUBMIT 
@app.route('/',methods=["POST"])
def results():
	#Get the salary
	salary = int(request.form['salary'])
	#Get the number of hours 
	number_of_hours = int(request.form['number_of_hours'])
	#Run the get_list_of_events() function 
	minutes_of_meetings = get_list_of_events()
	#Calculate the cost 
	cost = str(int(minutes_of_meetings*(salary*12/(54*number_of_hours*60))))
	return cost

if __name__ == '__main__':
    app.run(debug=True)