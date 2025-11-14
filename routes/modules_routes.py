from models import Course,CourseModule,UserRole
from flask import Blueprint,request,jsonify    
from app import db 
from auth import instructor_required
# from flask_jwt_extended import get_current_user
from auth import get_current_user

modules_bp = Blueprint("modules_bp",__name__)


@modules_bp.route("/")
def modules():
    return {
        "page":"mastercategories",
        "status":"🆗"
    }

#create modules 
""" create modules with courses    """
@modules_bp.route('/create-modules/<int:course_id>', methods=['POST'])
@instructor_required
def create_module(course_id):
    try:
        user = get_current_user()
        data = request.get_json()

        print(data)

        course = Course.query.get(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        

        if not data.get('title'):
            return jsonify({'error': 'Module title is required'}), 400
        
        # Get next order number
        max_order = db.session.query(db.func.max(CourseModule.order)).filter_by(course_id=course_id).scalar() or 0
        
        module = CourseModule(
            course_id=course_id,
            title=data['title'],
            description=data.get('description'),
            order=max_order + 1,
            duration_minutes=data.get('duration_minutes'),
            is_preview=data.get('is_preview', False)
        )
        
        db.session.add(module)
        db.session.commit()
        
        return jsonify({
            'message': 'Module created successfully',
            'module': module.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

# get modules 
""" get  all modules   """
@modules_bp.route('/get-modules', methods=['POST'])
@instructor_required
def list_modules_all():
    try:
        user = get_current_user()

        modules = CourseModule.query.all()

        return jsonify({
            'modules': [m.to_dict() for m in modules]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@modules_bp.route('/get-modules/<int:module_id>', methods=['POST'])
@instructor_required
def list_modules(module_id):
    try:
        user = get_current_user()

        module = CourseModule.query.get(module_id)

        if not module:
            return jsonify({'error': 'Module not found'}), 404

        return jsonify({
                    'module': module.to_dict(include_lessons=True)
                }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500




# update module 
""" Edit a Specific Module   """
@modules_bp.route('/update-modules/<int:module_id>', methods=['PUT'])
@instructor_required
def update_module(module_id):
    try:
        user = get_current_user()
        module = CourseModule.query.get(module_id)

        if not module :
            return jsonify({'error': ' module not found'}), 404


        data = request.get_json()

        if 'title' in data:
            module.title = data['title']
        if 'description' in data:
            module.description = data['description']
        if 'is_preview' in data:
            module.is_preview = data['is_preview']

        db.session.commit()

        return jsonify({
            'message': 'Module updated successfully',
            'module': module.to_dict(include_lessons=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# delete module 
""" Delete a Specific Module  """
@modules_bp.route('/delete-modules/<int:module_id>', methods=['DELETE'])
@instructor_required
def delete_module(module_id):
    try:
        user = get_current_user()
        module = CourseModule.query.get(module_id)

        if not module:
            return jsonify({'error': 'module not found'}), 404

        db.session.delete(module)
        db.session.commit()

        return jsonify({'message': 'Module deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

