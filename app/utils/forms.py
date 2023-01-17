from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired


class UploadFileForm(FlaskForm):
    file = FileField("Файл", validators=[InputRequired()])
    submit = SubmitField("Загрузить")
