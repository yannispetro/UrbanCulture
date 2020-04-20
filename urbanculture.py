from flask import Flask, render_template
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import InputRequired, Email, Length, AnyOf
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'PleaseDontTell'

class CityForm(Form):
    city = StringField('City', validators=[InputRequired()])

@app.route('/', methods= ['GET', 'POST'])
def index():
    form = CityForm()
    if form.validate_on_submit():
        return 'Form Successfully Submitted!'
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
