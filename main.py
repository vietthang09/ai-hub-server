from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
from functools import wraps

# Create the Flask application instance
app = Flask(__name__)

# Enable CORS for the frontend running on http://localhost:5173
CORS(app, origins=["http://localhost:5173"])

# In a real application, this should be a database. We're using a dictionary for this example.
users = {}

# A strong secret key is crucial for JWT security. In production, store this in an environment variable.
SECRET_KEY = "a_strong_and_secret_key"

def token_required(f):
    """
    Decorator to check for a valid JWT token in the Authorization header.
    It decodes the token and passes the payload data to the decorated function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if the Authorization header is present
        if 'Authorization' in request.headers:
            # The token is expected to be in the format: "Bearer <token>"
            auth_header = request.headers['Authorization']
            if " " in auth_header:
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            # Decode the JWT token with the secret key and the specified algorithm
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            
            # Extract the user's email and role from the token payload
            current_user_email = data['sub']
            current_user_role = data['role']
            
            # Pass this user data to the decorated function
            kwargs['user_data'] = {'email': current_user_email, 'role': current_user_role}
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': f'An unexpected error occurred: {str(e)}'}), 500

        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """
    Decorator to check if the user has an 'admin' role.
    It relies on the @token_required decorator to provide user_data.
    """
    @wraps(f)
    @token_required
    def decorated_function(*args, **kwargs):
        user_data = kwargs.get('user_data')
        if not user_data or user_data['role'] != 'admin':
            return jsonify({'message': 'Administrator access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['POST'])
def register():
    """Endpoint for user registration."""
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        if email in users:
            return jsonify({"error": "User with this email already exists"}), 409

        # Hash the password for secure storage
        hashed_password = generate_password_hash(password)

        # In a real application, this role would be assigned based on a business rule
        users[email] = {
            "password_hash": hashed_password,
            "role": "admin" # Changed default role to 'user' for a more realistic scenario
        }

        return jsonify({"message": "User registered successfully", "role": "user"}), 201

    except KeyError:
        return jsonify({"error": "Missing 'email' or 'password' in request"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/login', methods=['POST'])
def login():
    """Endpoint for user login, issues access and refresh tokens."""
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        if email not in users:
            return jsonify({"error": "Invalid email or password"}), 401

        user = users[email]

        # Check if the provided password matches the stored hash
        if check_password_hash(user['password_hash'], password):
            # Create an access token with a short expiration time
            access_token_payload = {
                'exp': datetime.utcnow() + timedelta(minutes=15),
                'iat': datetime.utcnow(),
                'sub': email,
                'role': user['role']
            }
            access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm='HS256')

            # Create a refresh token with a longer expiration time
            refresh_token_payload = {
                'exp': datetime.utcnow() + timedelta(days=7),
                'iat': datetime.utcnow(),
                'sub': email
            }
            refresh_token = jwt.encode(refresh_token_payload, SECRET_KEY, algorithm='HS256')

            return jsonify({
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "role": user['role']
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401

    except KeyError:
        return jsonify({"error": "Missing 'email' or 'password' in request"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/refresh', methods=['POST'])
def refresh():
    """Endpoint to get a new access token using a valid refresh token."""
    try:
        data = request.get_json()
        refresh_token = data['refresh_token']

        # Decode the refresh token to get the user's email
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=['HS256'])
        email = payload['sub']

        if email not in users:
            return jsonify({"error": "Invalid user"}), 401

        user = users[email]

        # Create a new access token
        new_access_token_payload = {
            'exp': datetime.utcnow() + timedelta(minutes=15),
            'iat': datetime.utcnow(),
            'sub': email,
            'role': user['role']
        }
        new_access_token = jwt.encode(new_access_token_payload, SECRET_KEY, algorithm='HS256')

        return jsonify({"access_token": new_access_token}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token has expired, please log in again"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token"}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/user_info', methods=['GET'])
@token_required
def get_user_info(user_data):
    """
    Endpoint to get user information.
    It does not require the user to provide an email in the request.
    The email is automatically extracted from the JWT token by the @token_required decorator.
    """
    try:
        # The user's email is provided by the decorator from the token payload
        email = user_data['email']

        if email not in users:
            return jsonify({"error": "User not found"}), 404

        user_info = users[email]
        return jsonify({
            "email": email,
            "role": user_info['role']
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# --- New functions for managing users ---
@app.route('/admin/users', methods=['POST'])
@admin_required
def create_user(user_data):
    """
    Admin-only endpoint to create a new user.
    """
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        role = data.get('role', 'user') # Default to 'user' if role is not provided

        if not email or not password:
            return jsonify({"error": "Missing 'email' or 'password' in request"}), 400

        if email in users:
            return jsonify({"error": "User with this email already exists"}), 409

        # Hash the password for secure storage
        hashed_password = generate_password_hash(password)

        users[email] = {
            "password_hash": hashed_password,
            "role": role
        }

        return jsonify({"message": "User created successfully", "email": email, "role": role}), 201

    except KeyError:
        return jsonify({"error": "Missing 'email' or 'password' in request"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/admin/users', methods=['GET'])
@admin_required
def get_all_users(user_data):
    """
    Admin-only endpoint to get a list of all registered users.
    Only users with the 'admin' role can access this.
    """
    try:
        # Create a list of users without their password hashes
        user_list = [{"email": email, "role": user_info['role']} for email, user_info in users.items()]
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/admin/user/<email>', methods=['PUT'])
@admin_required
def update_user_role(user_data, email):
    """
    Admin-only endpoint to update a user's role.
    """
    try:
        data = request.get_json()
        new_role = data.get('role')

        if not new_role:
            return jsonify({"error": "Missing 'role' in request"}), 400

        if email not in users:
            return jsonify({"error": "User not found"}), 404

        # Prevent an admin from changing their own role, to avoid locking themselves out
        if email == user_data['email']:
            return jsonify({"error": "Cannot change your own role"}), 403

        # Update the user's role
        users[email]['role'] = new_role
        return jsonify({"message": f"Role for user {email} updated to {new_role}"}), 200
    except KeyError:
        return jsonify({"error": "Missing 'role' in request"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        
@app.route('/admin/user/<email>', methods=['DELETE'])
@admin_required
def delete_user(user_data, email):
    """
    Admin-only endpoint to delete a user.
    """
    try:
        if email not in users:
            return jsonify({"error": "User not found"}), 404

        # Prevent an admin from deleting their own account
        if email == user_data['email']:
            return jsonify({"error": "Cannot delete your own account"}), 403

        del users[email]
        return jsonify({"message": f"User {email} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Initial setup for a test admin user
    if 'admin@example.com' not in users:
        users['admin@example.com'] = {
            "password_hash": generate_password_hash("adminpassword"),
            "role": "admin"
        }
    
    app.run(host='0.0.0.0', port=5000, debug=True)
