from lab3 import app, db
from flask import request, jsonify
from datetime import datetime
from lab3.schemas import Us_Sch, Cat_Sch, Rec_Sch, Curr_Sch
from lab3.models import User, Category, Record, Currency
from marshmallow.exceptions import ValidationError

with app.app_context():
    db.create_all()
    db.session.commit()

global_health_status = True

# ... (imports and database setup)

@app.route("/")
def greet_user():
    return f"<p>Greetings to the new user!</p><a href='/healthcheck'>Check Health</a>"

@app.route("/healthcheck")
def health_check():
    status_code = 200 if global_health_status else 500
    response = {
        "date": datetime.now(),
        "status": "OK" if global_health_status else "FAIL"
    }
    return jsonify(response), status_code

# User-related routes
@app.route('/user', methods=['POST'])
def create_custom_user():
    request_data = request.get_json()

    custom_user_schema = Us_Sch()
    try:
        user_data = custom_user_schema.load(request_data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    default_currency_id = request_data.get("default_currency_id")
    default_currency = Currency.query.filter_by(id=default_currency_id).first()

    if default_currency_id is None:
        default_currency = Currency.query.filter_by(name="Default Currency").first()
        if not default_currency:
            default_currency = Currency(name="Default Currency", symbol="USD")
            db.session.add(default_currency)
            db.session.commit()
            default_currency = Currency.query.filter_by(name="Default Currency").first()

    new_custom_user = User(
        username=user_data["username"],
        default_currency_id=default_currency.id
    )
    with app.app_context():
        db.session.add(new_custom_user)
        db.session.commit()

        user_response = {
            'id': new_custom_user.id,
            'username': new_custom_user.username,
            'currency': new_custom_user.default_currency.symbol if new_custom_user.default_currency else None
        }

        return jsonify(user_response), 200

@app.route('/user/<int:custom_user_id>', methods=['GET', 'DELETE'])
def manage_custom_user(custom_user_id):
    with app.app_context():
        custom_user = User.query.get(custom_user_id)

        if not custom_user:
            return jsonify({'error': f'This {custom_user_id} user does not exist'}), 404

        if request.method == "GET":
            user_data = {
                'id': custom_user.id,
                'username': custom_user.username,
                'currency': custom_user.default_currency_id
            }
            return jsonify(user_data), 200

        elif request.method == "DELETE":
            db.session.delete(custom_user)
            db.session.commit()
            return jsonify({'message': f'User {custom_user_id} deleted'}), 200

@app.route('/users', methods=['GET'])
def retrieve_all_custom_users():
    with app.app_context():
        custom_users_data = {
            custom_user.id: {"username": custom_user.username, "currency": custom_user.default_currency_id} for custom_user in User.query.all()
        }
        return jsonify(custom_users_data)

# Category-related routes
@app.route('/category', methods=['POST', 'GET'])
def manage_custom_category():
    if request.method == 'GET':
        with app.app_context():
            custom_categories_data = {
                custom_category.id: {"name": custom_category.name} for custom_category in Category.query.all()
            }
            return jsonify(custom_categories_data)

    elif request.method == 'POST':
        request_data = request.get_json()
        cat_schema = Cat_Sch()
        try:
            cat_data = cat_schema.load(request_data)
        except ValidationError as err:
            return jsonify({'error': err.messages}), 400

        new_custom_category = Category(name=cat_data["name"])
        with app.app_context():
            db.session.add(new_custom_category)
            db.session.commit()

            category_response = {
                "id": new_custom_category.id,
                "name": new_custom_category.name
            }

            return jsonify(category_response), 200

@app.route('/category/<int:custom_cat_id>', methods=['DELETE'])
def delete_custom_category(custom_cat_id):
    with app.app_context():
        custom_category = Category.query.get(custom_cat_id)

        if not custom_category:
            return jsonify({'error': f'Category {custom_cat_id} not found'}), 404

        db.session.delete(custom_category)
        db.session.commit()
        return jsonify({'message': f'Category {custom_cat_id} deleted'}), 200

# Record-related routes
@app.route('/records', methods=['GET'])
def retrieve_all_custom_records():
    with app.app_context():
        custom_records_data = {
            "records": [
                {
                    "id": custom_record.id,
                    "user_id": custom_record.user_id,
                    "cat_id": custom_record.category_id,
                    "amount": custom_record.amount,
                    "currency_id": custom_record.currency_id,
                    "created_at": custom_record.created_at
                } for custom_record in Record.query.all()
            ]
        }
        return jsonify(custom_records_data)

@app.route('/record', methods=['GET', 'POST'])
def manage_custom_records():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        category_id = request.args.get('category_id')

        if not user_id and not category_id:
            return jsonify({'error': 'Specify user_id or category_id'}), 400

        query = Record.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        if category_id:
            query = query.filter_by(category_id=category_id)

        custom_records = query.all()
        records_data = {
            custom_record.id: {
                "user_id": custom_record.user_id,
                "cat_id": custom_record.category_id,
                "amount": custom_record.amount,
                "currency_id": custom_record.currency_id,
                "created_at": custom_record.created_at
            } for custom_record in custom_records
        }
        return jsonify(records_data)

    elif request.method == 'POST':
        request_data = request.get_json()
        record_schema = Rec_Sch()
        try:
            record_data = record_schema.load(request_data)
        except ValidationError as err:
            return jsonify({'error': err.messages}), 400

        user_id = record_data['user_id']
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        currency_id = user.default_currency_id

        new_custom_record = Record(
            user_id=user_id,
            category_id=record_data['category_id'],
            amount=record_data['amount'],
            currency_id=currency_id
        )
        with app.app_context():
            db.session.add(new_custom_record)
            db.session.commit()

            record_response = {
                "id": new_custom_record.id,
                "user_id": new_custom_record.user_id,
                "cat_id": new_custom_record.category_id,
                "amount": new_custom_record.amount,
                "currency_id": new_custom_record.currency_id
            }

            return jsonify(record_response), 200

@app.route('/record/<int:custom_record_id>', methods=['GET', 'DELETE'])
def manage_custom_record(custom_record_id):
    with app.app_context():
        custom_record = Record.query.get(custom_record_id)

        if not custom_record:
            return jsonify({"error": f"Record {custom_record_id} not found"}), 404

        if request.method == "GET":
            record_data = {
                "id": custom_record.id,
                "user_id": custom_record.user_id,
                "cat_id": custom_record.category_id,
                "amount": custom_record.amount,
                "currency_id": custom_record.currency_id,
                "created_at": custom_record.created_at
            }
            return jsonify(record_data), 200

        elif request.method == "DELETE":
            db.session.delete(custom_record)
            db.session.commit()
            return jsonify({'message': f'Record {custom_record_id} deleted'}), 200

# Currency-related routes
@app.route('/currency', methods=['POST', 'GET'])
def manage_custom_currency():
    if request.method == 'GET':
        with app.app_context():
            custom_currencies_data = {
                custom_currency.id: {"name": custom_currency.name, "symbol": custom_currency.symbol}
                for custom_currency in Currency.query.all()
            }
            return jsonify(custom_currencies_data)

    elif request.method == 'POST':
        request_data = request.get_json()
        currency_schema = Curr_Sch()
        try:
            currency_data = currency_schema.load(request_data)
        except ValidationError as err:
            return jsonify({'error': err.messages}), 400

        new_custom_currency = Currency(name=currency_data["name"], symbol=currency_data["symbol"])
        with app.app_context():
            db.session.add(new_custom_currency)
            db.session.commit()

            currency_response = {
                "id": new_custom_currency.id,
                "name": new_custom_currency.name,
                "symbol": new_custom_currency.symbol
            }

            return jsonify(currency_response), 200

@app.route('/currency/<int:custom_currency_id>', methods=['GET', 'DELETE'])
def manage_custom_currency_by_id(custom_currency_id):
    with app.app_context():
        custom_currency = Currency.query.filter_by(id=custom_currency_id).first()

        if request.method == "GET":
            if custom_currency:
                currency_data = {
                    'id': custom_currency.id,
                    'name': custom_currency.name,
                    'symbol': custom_currency.symbol
                }
                return jsonify(currency_data), 200
            else:
                return jsonify({'error': f'Currency {custom_currency_id} not found'}), 404

        elif request.method == "DELETE":
            if custom_currency:
                db.session.delete(custom_currency)
                db.session.commit()
                return jsonify({'message': f'Currency {custom_currency_id} deleted'}), 200
            else:
                return jsonify({'error': f'Currency {custom_currency_id} not found'}), 404
