from flask import request,Blueprint,jsonify
from models import MasterCategory,SubCategory,Course,Enrollment
from auth import get_current_user



public_bp = Blueprint("public",__name__)


@public_bp.route("/")
def public():
    return {
        "page":"public",
        "status":"🆗"
    }


"""Get all the Master Course with specific id including subcategories """
@public_bp.route("/get-mastercategories/<int:category_id>", methods=["POST"])
def get_master_category(category_id):
    try:
        category = MasterCategory.query.get_or_404(category_id)
        
        include_courses = request.args.get("courses", "false").lower() == "true"  # parse bool safely

        return jsonify(category.to_dict(include_subcategories=True,include_courses=include_courses)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400




"""Get master Categories only"""
@public_bp.route('/get-mastercategories', methods=['POST'])
def get_master_categories_only():   
    try:
        include_subcategories=request.args.get("subcategories")
        
        categories = MasterCategory.query.all()
        count = len(categories)
        
        categories = [
            cat.to_dict(include_subcategories=include_subcategories)
            if include_subcategories is not None else cat.to_dict()
            for cat in categories
        ]

        return jsonify({
            "message": "Master categories fetched successfully",
            "count": count,
            "categories": categories
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




# ✅ GET all subcategories
"""Get All Subcategories with courses"""
@public_bp.route("/get-subcategories", methods=["POST"])
def get_all_subcategories():
    try:
        include_courses=request.args.get("courses")
        subcategories = SubCategory.query.all()
        return jsonify([sub.to_dict(include_courses=True)  if include_courses is not None else sub.to_dict() for sub in subcategories]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

    
# ✅ GET single subcategory by ID
""" GET single subcategory by ID"""
@public_bp.route("/get-subcategories/<int:subcategory_id>", methods=["POST"])
def get_subcategory(subcategory_id):
    try:
        subcategory = SubCategory.query.get_or_404(subcategory_id)
        return jsonify(subcategory.to_dict(include_courses=True)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    



# get specific course
""" get a specific course   """
@public_bp.route('/get-courses/<int:course_id>', methods=['POST'])
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
        # Remove video_url from all lessons if not enrolled, unless it's a preview
        modules = course_data.get('modules', [])

        for module in modules:
            lessons = module.get('lessons', [])
            for lesson in lessons:
                lesson.pop('video_url', None)

        course_data['is_enrolled'] = is_enrolled
        
        return jsonify({'course': course_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@public_bp.route('/get-courses', methods=['POST'])
def get_courses_all():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', '10')  # keep as string to check for 'all'
        search = request.args.get('search', '', type=str).strip()

        # Base query
        query = Course.query

        # 🔍 Add search filter
        if search:
            from app import db 
            like_pattern = f"%{search}%"
            query = query.filter(
                db.or_(
                    Course.title.ilike(like_pattern),
                    Course.description.ilike(like_pattern),
                    Course.short_description.ilike(like_pattern)
                )
            )

        query = query.order_by(Course.created_at.desc())

        # If per_page == 'all', return all records without pagination
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

        # Normal paginated result
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

