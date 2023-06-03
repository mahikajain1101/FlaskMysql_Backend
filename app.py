from flask import Flask, jsonify, request
from flask_mysqldb import MySQL

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Wearemm@123'
app.config['MYSQL_DB'] = 'backend2'

app.config["JWT_SECRET_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5c" 
jwt = JWTManager(app)

mysql = MySQL(app)


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(409)
def conflict(error):
    return jsonify({'error': 'Conflict'}), 409


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        cur.close()

        users = []
        for row in rows:
            user = {
                'id': row[0],
                'name': row[1],
                'email': row[2]
            }
            users.append(user)

        return jsonify(users)
    except Exception as e:
        return internal_error(e)


@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        cur.close()

        if row:
            user = {
                'id': row[0],
                'name': row[1],
                'email': row[2]
            }
            return jsonify(user)
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return internal_error(e)


@app.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    try:
        data = request.get_json()
        name = data['name']
        email = data['email']

        if not name or not email:
            return jsonify({'error': 'Name and email are required'}), 400

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409

        cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'User created successfully'})
    except Exception as e:
        return internal_error(e)


@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        data = request.get_json()
        name = data['name']
        email = data['email']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET name = %s, email = %s WHERE id = %s", (name, email, user_id))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        return internal_error(e)


@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user_by_id(user_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        return internal_error(e)


@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != "test" or password != "test":
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


if __name__ == '__main__':
    app.run(port='5001', debug=True)
