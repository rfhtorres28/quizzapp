from flask_wtf import FlaskForm
from wtforms import RadioField, HiddenField
from wtforms.validators import InputRequired
from ECEbank import ece_questions


class QuizForm(FlaskForm):

    q1_choices = [option for option in ece_questions[0]['options']]
    q2_choices = [option for option in ece_questions[1]['options']]
    q3_choices = [option for option in ece_questions[2]['options']]

    q1 = RadioField(ece_questions[0], choices=q1_choices, validators=[InputRequired()])
    q2 = RadioField(ece_questions[1], choices=q2_choices, validators=[InputRequired()])
    q3 = RadioField(ece_questions[2], choices=q3_choices, validators=[InputRequired()])

    user_id = HiddenField()