from flask import Blueprint, request, jsonify
from extensions import db
from src.models.sql_models import User
from src.auth.utils import generate_jwt_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()

        language = data.get('language', 'ru')
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            error_msg = 'Username already exists' if language == 'en' else 'Имя пользователя уже существует'
            return jsonify({'error': error_msg}), 409
        if User.query.filter_by(email=data['email']).first():
            error_msg = 'Email already exists' if language == 'en' else 'Email уже существует'
            return jsonify({'error': error_msg}), 409
        
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate token for new user
        token = generate_jwt_token(new_user.id)
        
        return jsonify({
            'message': 'User created successfully' if language == 'en' else 'Пользователь успешно создан',
            'token': token,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        error_msg = 'Registration failed' if language == 'en' else 'Ошибка регистрации'
        return jsonify({'error': error_msg, 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        language = data.get('language', 'ru')
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.check_password(data['password']):
            token = generate_jwt_token(user.id)
            return jsonify({
                'message': 'Login successful' if language == 'en' else 'Вход выполнен успешно',
                'token': token,
                'user': user.to_dict()
            })
        else:
            error_msg = 'Invalid username or password' if language == 'en' else 'Неверное имя пользователя или пароль'
            return jsonify({'error': error_msg}), 401
            
    except Exception as e:
        error_msg = 'Login failed' if language == 'en' else 'Ошибка входа'
        return jsonify({'error': error_msg, 'details': str(e)}), 500