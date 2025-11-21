from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Course, CourseModule, Lesson, User, Enrollment, UserRole, CourseStatus,MasterCategory,SubCategory,CoursePrerequisitesCourses,ModeOfConduct
from auth import get_current_user, instructor_required
from utils.validators import validate_course_data
from werkzeug.utils import secure_filename
import uuid 
import os 
from models import db, LessonResource,CourseModule
from datetime import datetime
from services.file_service import FileService
from dotenv import load_dotenv
load_dotenv()
file_service = FileService()

course_bp = Blueprint('courses', __name__)


@course_bp.route("/")
def courses():
    return {
        "page":"mastercategories",
        "status":"🆗"
    }


# UPLOAD_FOLDER = 'static/uploads/thumbnails/'  # Or wherever you want
UPLOAD_FOLDER = "thumbnails"   # Or wherever you want
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','svg'}


"""Get courses such as archived, draft, published """
# get courses 
@course_bp.route('get-courses/', methods=['POST'])
def get_courses():
    try:
        data = request.get_json()
        types = ["published", "draft", "archived"]
        status = data.get('status', '').lower()

        # Start with base query
        query = Course.query

        # Status filtering
        if status:
            if status in types:
                query = query.filter_by(status=CourseStatus(status))
            elif status != 'all':
                return {"error": f"Invalid status: {status}"}

        # Optional filters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        difficulty = request.args.get('difficulty')
        instructor_id = request.args.get('instructor_id', type=int)
        search = request.args.get('search')

        if difficulty:
            query = query.filter_by(difficulty_level=difficulty)

        if instructor_id:
            query = query.filter_by(instructor_id=instructor_id)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Course.title.ilike(search_term),
                    Course.description.ilike(search_term),
                    Course.short_description.ilike(search_term)
                )
            )

        # Final query execution
        courses = query.order_by(Course.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'courses': [course.to_dict() for course in courses.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': courses.total,
                'pages': courses.pages,
                'has_next': courses.has_next,
                'has_prev': courses.has_prev
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@course_bp.route('/get-courses', methods=['POST'])
def get_courses_all():
    try:
        # You’re using POST, but pagination parameters usually come from query params.
        # So we’ll still read them safely from args (URL), but you can switch to JSON if needed.
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', '10')  # keep as string to check for 'all'

        query = Course.query.order_by(Course.created_at.desc())

        # ✅ If per_page == 'all', return all records without pagination
        if per_page == 'all':
            courses = query.all()
            return jsonify({
                "courses": [course.to_dict() for course in courses],
                "pagination": {
                    "page": 1,
                    "per_page": "all",
                    "total_pages": 1,
                    "total_items": len(courses),
                    "has_next": False,
                    "has_prev": False
                }
            }), 200

        # Convert per_page to integer for normal pagination
        per_page = int(per_page)

        # ✅ Normal paginated result
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        courses = pagination.items

        return jsonify({
            "courses": [course.to_dict() for course in courses],
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total_pages": pagination.pages,
                "total_items": pagination.total,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# get specific course
""" get a specific course   """
@course_bp.route('/get-courses/<int:course_id>', methods=['POST'])
def get_course(course_id):
    try:
        course = Course.query.get(course_id)
        include_lessons = request.args.get("lessons", "false").lower() == "true"  # parse bool safely
        include_resources = request.args.get("resources", "false").lower() == "true"

        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Check if user is enrolled (if authenticated)
        user = get_current_user()
        is_enrolled = False
        if user:
            enrollment = Enrollment.query.filter_by(
                user_id=user.id, 
                course_id=course_id, 
                is_active=True
            ).first()
            is_enrolled = enrollment is not None
        
        course_data = course.to_dict(include_modules=True,include_lessons=include_lessons,include_resources=include_resources)
        course_data['is_enrolled'] = is_enrolled
        
        return jsonify({'course': course_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


"""Create courses with subcategory id """
# creating courses 
@course_bp.route('/create-courses', methods=['POST'])
@instructor_required
def create_course():
    print("Create Course Route hit---")
    
    print("FORM DATA:", request.form)
    print("FILES:", request.files)


    user = get_current_user()
    data = request.form  # ✅ Get non-file fields from form data
    file = request.files.get('thumbnail')  # ✅ Get uploaded file
    
    subcategory_id = data.get("subcategory_id")

    if subcategory_id:
        try:
            subcategory_id = int(subcategory_id)
            # Optional: validate if subcategory exists
            subcategory = SubCategory.query.get(subcategory_id)
            if not subcategory:
                return jsonify({'error': f"Invalid subcategory_id: {subcategory_id}"}), 400
        except ValueError:
            return jsonify({'error': "subcategory_id must be an integer"}), 400
    else:
        subcategory_id = None  # or default
    
    # Optional: validate required fields
    required_fields = ['title', 'price']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    # Handle thumbnail upload if provided
    thumbnail_path = None
    global UPLOAD_FOLDER
    if file and file_service.validate_file_type(file.filename,allowed_extensions=ALLOWED_EXTENSIONS):  # Make sure `allowed_file` checks file extension
        relative_path, file_size = file_service.save_file(file=file,subfolder=UPLOAD_FOLDER)
    else:
        relative_path = None

    if data.get('status'):
        try:
            status = CourseStatus(data['status'].lower())
        except ValueError:
            return jsonify({'error': f"Invalid role: {data['role']}"}), 400
    else:
        status = CourseStatus.DRAFT

    if data.get('mode_of_conduct'):
        try:
            mode_of_conduct = ModeOfConduct(data['mode_of_conduct'].lower())
        except Exception as e:
            return jsonify({'error': f"Invalid mode : {data['mode_of_conduct']}"}), 400
            
    else:
        mode_of_conduct =  ModeOfConduct.OFFLINE

    if status == CourseStatus.PUBLISHED:
        is_active = True
    else:
        is_active = False

        
    # Create course
    course = Course(
        title=data.get('title'),
        description=data.get('description'),
        short_description=data.get('short_description'),
        instructor_id=user.id,
        subcategory_id=subcategory_id,
        price=float(data.get('price')),
        currency=data.get('currency', 'USD'),
        duration_hours=data.get('duration_hours'),
        difficulty_level=data.get('difficulty_level'),
        thumbnail=relative_path,
        max_students=int(data.get('max_students', 0)) if data.get('max_students') else None,
        prerequisites=data.get('prerequisites'),
        status=status,
        learning_outcomes=data.get('learning_outcomes'),
        is_active =  is_active,
        mode_of_conduct =  mode_of_conduct 
    )

    db.session.add(course)
    db.session.commit()

    return jsonify({
        'message': 'Course created successfully',
        'course': course.to_dict(include_modules=True)
    }), 201

    # except Exception as e:
    #     db.session.rollback()
    #     return jsonify({'error': str(e)}), 500
# edit specific course 

"""Edit a Specific course """
@course_bp.route('/update-courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    try:
        user = get_current_user()
        course = Course.query.get(course_id)

        if not course:
            return jsonify({'error': 'Course not found'}), 404

        # ✅ Role check
        if not (
            user.role == UserRole.ADMIN or
            (user.role == UserRole.INSTRUCTOR and course.instructor_id == user.id)
        ):
            return jsonify({'error': 'Unauthorized to update this course'}), 403

        # ✅ Handle both JSON + form-data
        if request.content_type and "application/json" in request.content_type:
            data = request.get_json()
            file = None
        else:
            data = request.form
            file = request.files.get('thumbnail')
        
        print("content_type:",request.content_type)
        print("data:",data)
        print("file:",file)
        
        # ✅ Update only if provided (no "title is required" check here)
        if data.get('title'):
            course.title = data['title']
        if data.get('description'):
            course.description = data['description']
        if data.get('short_description'):
            course.short_description = data['short_description']
        if data.get('price'):
            course.price = float(data['price'])
        if data.get('currency'):
            course.currency = data['currency']
        if data.get('duration_hours'):
            course.duration_hours = data['duration_hours']
        if data.get('difficulty_level'):
            course.difficulty_level = data['difficulty_level']
        if data.get('max_students'):
            course.max_students = int(data['max_students'])
        if data.get('prerequisites'):
            course.prerequisites = data['prerequisites']
        if data.get('learning_outcomes'):
            course.learning_outcomes = data['learning_outcomes']
        if data.get('subcategory_id'):
            course.subcategory_id = int(data['subcategory_id'])

        # ✅ Status update
        if data.get('status') and user.role in [UserRole.ADMIN, UserRole.INSTRUCTOR]:
            try:
                course.status = CourseStatus(data['status'].lower())
            except ValueError:
                return jsonify({'error': f"Invalid status: {data['status']}"}), 400

        # ✅ Handle prerequisites mapping (many-to-many table)
        if "prerequisite_course_ids" in data:
            CoursePrerequisitesCourses.query.filter_by(course_id=course.id).delete()
            for pid in data["prerequisite_course_ids"]:
                db.session.add(
                    CoursePrerequisitesCourses(course_id=course.id, prerequisite_course_id=pid)
                )
        # print("Uploaded file:", file.filename)
        # print("Valid:", file_service.validate_file_type(file.filename, allowed_extensions=ALLOWED_EXTENSIONS))

        # ✅ Handle thumbnail upload
        # if file and file_service.validate_file_type(file.filename,allowed_extensions=ALLOWED_EXTENSIONS):
        #     if file_service.delete_file(course.thumbnail):
        #         relative_path, file_size = file_service.save_file(file,subfolder=UPLOAD_FOLDER)
        #         course.thumbnail = relative_path 

        if file and file_service.validate_file_type(file.filename, allowed_extensions=ALLOWED_EXTENSIONS):
            # Delete old file ONLY if it exists
            if course.thumbnail:
                file_service.delete_file(course.thumbnail)

            # Always save the new file
            relative_path, file_size = file_service.save_file(file, subfolder=UPLOAD_FOLDER)
            course.thumbnail = relative_path

        
        db.session.commit()

        return jsonify({
            'message': 'Course updated successfully',
            'course': course.to_dict(include_modules=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

"""  delete courses   """
#delete course 
@course_bp.route('/delete-courses/<int:course_id>', methods=['DELETE'])
@instructor_required
def delete_course(course_id):
    try:
        user = get_current_user()
        course = Course.query.get(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Check if user owns the course or is admin
        if course.instructor_id != user.id and user.role != UserRole.ADMIN:
            return jsonify({'error': 'Unauthorized to delete this course'}), 403
        
        # Check if course has enrollments
        if course.enrollments.count() > 0:
            return jsonify({'error': 'Cannot delete course with active enrollments'}), 400
        
        file_service.delete_file(course.thumbnail)
        db.session.delete(course)
        db.session.commit()
        
        return jsonify({'message': 'Course deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500





""" get your courses  """
@course_bp.route('/my-courses', methods=['POST'])
@instructor_required
def get_my_courses():
    try:
        user = get_current_user()
        
        # Get courses based on user role
        if user.role == UserRole.ADMIN:
            courses = Course.query.all()
        else:
            courses = Course.query.filter_by(instructor_id=user.id).all()
        
        return jsonify({
            'courses': [course.to_dict(include_modules=True) for course in courses]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# target-1 start from here 10 sept 
@course_bp.route('publish-courses/<int:course_id>/publish', methods=['PATCH'])
@instructor_required
def publish_course(course_id):
    try:
        user = get_current_user()
        course = Course.query.get(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Check if user owns the course or is admin
        if course.instructor_id != user.id and user.role != UserRole.ADMIN:
            return jsonify({'error': 'Unauthorized to publish this course'}), 403
        
        # Validate course is ready for publishing
        if not course.modules.count():
            return jsonify({'error': 'Course must have at least one module to be published'}), 400
        
        has_lessons = any(module.lessons.count() > 0 for module in course.modules)
        if not has_lessons:
            return jsonify({'error': 'Course must have at least one lesson to be published'}), 400
        
        course.status = CourseStatus.PUBLISHED
        db.session.commit()
        
        return jsonify({
            'message': 'Course published successfully',
            'course': course.to_dict(include_modules=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    


# get enrollments for specific course id 
@course_bp.route('/<int:course_id>/enrollments', methods=['POST'])
@instructor_required
def get_course_enrollments(course_id):
    try:
        user = get_current_user()
        course = Course.query.get(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Check if user owns the course or is admin     
        if course.instructor_id != user.id and user.role != UserRole.ADMIN:
            return jsonify({'error': 'Unauthorized to view course enrollments'}), 403
        
        enrollments = Enrollment.query.filter_by(course_id=course_id, is_active=True).all()
        
        enrollment_data = []
        for enrollment in enrollments:
            user_data = enrollment.user.to_dict()
            enrollment_info = enrollment.to_dict()
            enrollment_data.append({
                'user': user_data,
                'enrollment': enrollment_info
            })
        
        return jsonify({
            'course_id': course_id,
            'course_title': course.title,
            'total_enrollments': len(enrollment_data),
            'enrollments': enrollment_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



