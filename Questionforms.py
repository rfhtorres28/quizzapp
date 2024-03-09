from flask_wtf import FlaskForm
from wtforms import RadioField, HiddenField
from wtforms.validators import DataRequired
from ECEbank import ece_questions


class QuizForm(FlaskForm):

    q1_choices = [(option['letter'], option['content']) for option in ece_questions[0]['options']]
    q2_choices = [(option['letter'], option['content']) for option in ece_questions[1]['options']]
    q3_choices = [(option['letter'], option['content']) for option in ece_questions[2]['options']]

    q1 = RadioField(ece_questions[0], choices=q1_choices, validators=[DataRequired()])
    q2 = RadioField(ece_questions[1], choices=q2_choices, validators=[DataRequired()])
    q3 = RadioField(ece_questions[2], choices=q3_choices, validators=[DataRequired()])

    user_id = HiddenField()