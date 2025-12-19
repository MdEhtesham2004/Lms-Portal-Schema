# crud for ContactForm
from flask import Blueprint, request, jsonify
from models import ContactForm 
from app import db
import requests

contact_bp = Blueprint('contact_routes', __name__)

@contact_bp.route('/contact-forms', methods=['POST'])
def create_contact_form():
    data = request.get_json()
    if not data or not all(key in data for key in ['name', 'email','phone_number']):
        return jsonify({'error': 'Missing data'}), 400
    
    new_form = ContactForm(
        name=data['name'],
        email=data['email'],
        phone_number=data.get('phone_number'),  
        message=data['message'] if data.get('message') else None,
        course_interest=data.get('course_interest') if data.get('course_interest') else None
    )
    db.session.add(new_form)
    db.session.commit()
    return jsonify(new_form.to_dict()), 201

@contact_bp.route('/contact-forms', methods=['GET'])
def get_contact_forms():
    forms = ContactForm.query.all()
    return jsonify([form.to_dict() for form in forms]), 200

@contact_bp.route('/contact-forms/<int:form_id>', methods=['GET'])
def get_contact_form(form_id):
    form = ContactForm.query.get_or_404(form_id)
    return jsonify(form.to_dict()), 200

@contact_bp.route('/contact-forms/<int:form_id>', methods=['PUT'])
def update_contact_form(form_id):
    form = ContactForm.query.get_or_404(form_id)
    data = request.get_json()
    
    if 'name' in data:
        form.name = data['name']
    if 'email' in data:
        form.email = data['email']
    if 'message' in data:
        form.message = data['message']
    if 'phone_number' in data:
        form.phone_number = data['phone_number']
    if 'course_interest' in data:
        form.course_interest = data['course_interest']
    
    db.session.commit()
    return jsonify(form.to_dict()), 200

@contact_bp.route('/contact-forms/<int:form_id>', methods=['DELETE'])
def delete_contact_form(form_id):
    form = ContactForm.query.get_or_404(form_id)
    db.session.delete(form)
    db.session.commit()
    return jsonify({'message': 'Contact form deleted'}), 204
