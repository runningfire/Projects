import flask 
app = flask(__name__)


@app.route('/')
def index():
	return 'Hi!'
if __name__== '__main__':
	app.run()	

