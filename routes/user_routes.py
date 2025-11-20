from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, Enrollment, Course, LessonProgress, Certificate,Payment,PaymentStatus
from auth import get_current_user
from utils.validators import validate_email
from services.email_service import EmailService
user_bp = Blueprint('users', __name__)

email_service = EmailService()

# get profile details 
"""GET profile Details """
@user_bp.route('/get-profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# update user details 
"""Edit Profile Details"""
@user_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'bio' in data:
            user.bio = data['bio']
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']
        
        # Validate email if provided
        if 'email' in data:
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=data['email'].lower()).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': 'Email already taken'}), 409
            
            user.email = data['email'].lower()
            user.email_verified = False  # Need to re-verify email
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


""" Get Student Certificates  """
@user_bp.route('/get-certificates', methods=['GET'])
@jwt_required()
def get_certificates():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        certificates = Certificate.query.filter_by(user_id=user.id).all()
        
        return jsonify({
            'certificates': [cert.to_dict() for cert in certificates]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

"""Get Student Dashboard"""
@user_bp.route('/get-dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get active enrollments
        enrollments = Enrollment.query.filter_by(user_id=user.id, is_active=True).all()
        
        
        # Get certificates
        certificates = Certificate.query.filter_by(user_id=user.id).all()

        payments = Payment.query.filter_by(user_id=user.id).all()
        
        # Calculate statistics
        total_courses = len(enrollments)
        completed_courses = len([e for e in enrollments if e.completed_at])
        in_progress_courses = total_courses - completed_courses
        total_certificates = len(certificates)
        
        # Get recent activity (last 5 enrollments)
        recent_enrollments = Enrollment.query.filter_by(user_id=user.id, is_active=True)\
            .order_by(Enrollment.enrolled_at.desc()).limit(5).all()
        
        recent_activity = []
        for enrollment in recent_enrollments:
            course_data = enrollment.course.to_dict()
            course_data['enrollment'] = enrollment.to_dict()
            recent_activity.append(course_data)
        
        return jsonify({
            'user': user.to_dict(),
            'statistics': {
                'total_courses': total_courses,
                'completed_courses': completed_courses,
                'in_progress_courses': in_progress_courses,
                'total_certificates': total_certificates
            },
            'recent_activity': recent_activity,
            'certificates': [cert.to_dict() for cert in certificates],
            'payments':[payment.to_dict() for payment in payments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500





