from flask_wtf import FlaskForm
from wtforms import RadioField, HiddenField
from wtforms.validators import InputRequired
from ECEbank import ece_questions


class QuizForm(FlaskForm):
    user_id = HiddenField()

def create_dynamic_fields(questions):
    for i, question in enumerate(questions, start=1):
        choices = [(option['letter'], option['content']) for option in question['options']]
        field_name = f'q{i}'
        field_label = question['content']
        setattr(QuizForm, field_name, RadioField(field_label, choices=choices, validators=[InputRequired()]))

create_dynamic_fields(ece_questions)