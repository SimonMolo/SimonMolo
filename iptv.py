import os
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, url_for, request
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from pymysql import IntegrityError
from wtforms import DateField, HiddenField, StringField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import InputRequired
from datetime import datetime, timedelta
from twilio.rest import Client


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Récupérer les valeurs des variables d'environnement
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
current_date = datetime.utcnow().date()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    SubscribeDate = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    parrain_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    parrain = db.relationship('User', remote_side=[id], backref='filleuls')
    commentaire = db.Column(db.Text, nullable=False)
    fournisseur = db.Column(db.String(255), default='', nullable=True)

    def __init__(self, name, SubscribeDate, phone, is_active=True, parrain=None, commentaire='', fournisseur=''):
        self.name = name
        self.SubscribeDate = SubscribeDate
        self.phone = phone
        self.is_active = is_active
        self.parrain = parrain
        self.commentaire = commentaire
        self.fournisseur = fournisseur

    def subscription_end_date(self):
        return self.SubscribeDate + timedelta(days=180)

class Filleul(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filleul_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=[user_id], backref='relations_user')
    filleul = db.relationship('User', foreign_keys=[filleul_id], backref='relations_filleul')


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    phone = StringField('Phone', validators=[InputRequired()])
    subscribe_date = DateField('Subscribe Date', validators=[InputRequired()])
    is_active = BooleanField('Account is Active')
    parrain_name = StringField('Parrain Name')
    commentaire = TextAreaField('Commentaire')
    fournisseur = StringField('Fournisseur', validators=[InputRequired()])
    submit = SubmitField('Add User')


class EditUserForm(FlaskForm):
    user_id = HiddenField()
    name = StringField('Name', validators=[InputRequired()])
    subscribe_date = DateField('Subscribe Date', validators=[InputRequired()])
    phone = StringField('Phone', validators=[InputRequired()])
    is_active = BooleanField('Account is Active')
    parrain_name = StringField('Parrain Name')
    commentaire = TextAreaField('Commentaire')
    submit = SubmitField('Update User')
    fournisseur = StringField('Fournisseur', validators=[InputRequired()])

    def populate_obj(self, obj):
        # Utilisez les valeurs existantes comme placeholders
        for field in self:
            if field.name not in ('csrf_token', 'submit', 'user_id'):
                # Utilisez le champ.raw_data pour récupérer la valeur d'origine du champ
                raw_data = field.raw_data
                if raw_data:
                    # Utilisez render_kw pour définir le placeholder
                    field.render_kw = {'placeholder': raw_data[0]}
        super().populate_obj(obj)


def send_sms(to, message):
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        body=message,
        from_=twilio_phone_number,
        to=to
    )

with app.app_context():
    # Vos opérations liées à la base de données ici
    # Notez que vous devez spécifier un ID d'utilisateur existant, car User.query.filter_by(id=User.id).first() ne retournera pas ce que vous attendez.
    user = User.query.get(1)  # Remplacez 1 par l'ID de l'utilisateur souhaité
    if user:
        subscription_end_date = user.SubscribeDate + timedelta(days=180)  # 180 jours pour 6 mois

        # Vérifiez si la fin de l'abonnement est dans 10 jours
        current_date = datetime.now().date()
        if subscription_end_date - current_date == timedelta(days=10):
            message = f"L'abonnement de {user.name} expire le {subscription_end_date}, le rappeler au {user.phone}"
            send_sms(twilio_phone_number, message)
    else:
        print("Utilisateur non trouvé.")

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/users')
def show_users():
    # Récupérer les paramètres de tri et de recherche depuis l'URL
    sort_by = request.args.get('sort_by', 'alphabetical')
    search_term = request.args.get('search', '')

    # Construction de la requête en fonction des paramètres
    query = User.query.filter(or_(User.name.ilike(f'%{search_term}%')))

    if sort_by == 'subscription_date':
        users = query.order_by(User.SubscribeDate).all()
    elif sort_by == 'subscription_end_date':
        users = query.order_by(User.SubscribeDate + timedelta(days=180)).all()
    else:  # Tri par défaut (alphabétique)
        users = query.order_by(User.name).all()

    return render_template('users.html', users=users)


@app.route('/user/<int:user_id>')
def user_detail(user_id):
    user = User.query.get(user_id)

    if user is not None:
        subscription_end_date = user.SubscribeDate + timedelta(days=180)  # 180 jours pour 6 mois
        # Reste du code pour vérifier l'expiration de l'abonnement, etc.
        return render_template('user_detail.html', user=user, end_subscription_date=subscription_end_date)
    else:
        # Gérer le cas où l'utilisateur n'est pas trouvé
        print("Utilisateur non trouvé.")
        return render_template('user_not_found.html')
    
@app.route('/get_suggestions', methods=['POST'])
def get_suggestions():
    input_text = request.form.get('input')

    # Remplacez cette logique par la récupération des suggestions depuis votre base de données
    suggestions = ["Suggestion1", "Suggestion2", "Suggestion3"]

    # Retournez les suggestions sous forme de réponse JSON
    return jsonify(suggestions)

@app.route('/get_parrain_suggestions', methods=['POST'])
def get_parrain_suggestions():
    input_text = request.form.get('input')

    # Remplacez cette logique par la récupération des suggestions depuis votre base de données
    suggestions = User.query.filter(User.name.ilike(f"%{input_text}%")).all()

    # Retournez les suggestions sous forme de réponse JSON
    return jsonify([user.name for user in suggestions])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Vérifiez si l'utilisateur avec le même nom existe déjà
            existing_user = User.query.filter_by(name=form.name.data).first()

            if existing_user:
                flash('User with the same name already exists', 'danger')
            else:
                user = User(
                    name=form.name.data,
                    SubscribeDate=form.subscribe_date.data,
                    phone=form.phone.data,
                    is_active=form.is_active.data,
                    commentaire=form.commentaire.data,
                    fournisseur=form.fournisseur.data
                )

                parrain_name = form.parrain_name.data
                if parrain_name:
                    parrain = User.query.filter_by(name=parrain_name).first()
                    if parrain:
                        user.parrain = parrain
                        parrain.filleuls.append(user)

                db.session.add(user)
                db.session.commit()
                flash('User added successfully', 'success')
                return redirect(url_for('show_users'))

        except IntegrityError as e:
            db.session.rollback()
            flash('Error: ' + str(e), 'danger')

    return render_template('register.html', form=form)

# Utilisez le nouveau formulaire pour la modification
@app.route('/edit_user_route/<int:user_id>', methods=['GET', 'POST'])
def edit_user_route(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    if request.method == 'POST' and form.validate_on_submit():
        form.user_id.data = user_id  # Ajouter user_id au formulaire
        form.populate_obj(user)
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('show_users'))


    return render_template('edit_user_route.html', form=form, user=user)



@app.route('/delete_user_route/<int:user_id>', methods=['GET', 'POST'])
def delete_user_route(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
        return redirect(url_for('show_users'))


if __name__ == '__main__':
    with app.app_context():
        if not db.engine.has_table(User.__tablename__):
            db.create_all()

    app.run(debug=True)
