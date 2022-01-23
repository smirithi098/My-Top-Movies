from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField
from wtforms.validators import DataRequired


class AddForm(FlaskForm):
    movie_field = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


class EditForm(FlaskForm):
    rating_field = DecimalField('Your Rating out of 10 e.g: 7.5', validators=[DataRequired()])
    review_field = StringField('Your Review', validators=[DataRequired()])
    done_btn = SubmitField('Done')
