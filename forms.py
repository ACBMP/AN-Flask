
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms import BooleanField
from wtforms.validators import DataRequired


class PlayerForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    igns = StringField('igns')
    tw_handle = StringField('tw_handle')
    nation = StringField('nation')
    pl_pc = BooleanField('pl_pc')
    pl_ps3 = BooleanField('pl_ps3')
    pl_xbox = BooleanField('pl_xbox')
    submit = SubmitField('Submit')
