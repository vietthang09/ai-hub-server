from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

users = {}

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        if email in users:
            return jsonify({"error": "User with this email already exists"}), 409

        hashed_password = generate_password_hash(password)

        users[email] = {
            "password_hash": hashed_password,
            "role": "admin"
        }

        return jsonify({"message": "User registered successfully", "role": "admin"}), 201

    except KeyError:
        return jsonify({"error": "Missing 'email' or 'password' in request"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        if email not in users:
            return jsonify({"error": "Invalid email or password"}), 401

        user = users[email]

        if check_password_hash(user['password_hash'], password):
            return jsonify({"message": "Login successful", "role": user['role']}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401

    except KeyError:
        return jsonify({"error": "Missing 'email' or 'password' in request"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
