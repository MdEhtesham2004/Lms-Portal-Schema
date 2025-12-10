from flask import request, Blueprint, jsonify,session
from models import MasterCategory, SubCategory, Course, Enrollment
from auth import get_current_user
from app import limiter



public_bp = Blueprint("public", __name__)


@public_bp.route("/")
# @limiter.limit("10 per minute")
def public():
    return {
        "page":"public",
        "status":"🆗"
    }


"""Get all the Master Course with specific id including subcategories """
@public_bp.route("/get-mastercategories/<int:category_id>", methods=["POST"])
@limiter.limit("60 per minute")
def get_master_category(category_id):
    try:
        category = MasterCategory.query.get_or_404(category_id)
        
        include_courses = request.args.get("courses", "false").lower() == "true"  # parse bool safely

        return jsonify(category.to_dict(include_subcategories=True,include_courses=include_courses)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@public_bp.route('/get-mastercategories', methods=['POST'])
def get_master_categories_only():   
    try:
        include_subcategories = request.args.get("subcategories")
        include_courses = request.args.get("courses")
        
        # Normalize boolean flag
        is_courses_requested = (include_courses == "true")

        categories = MasterCategory.query.all()
        count = len(categories)
        
        # 1. Get the base dictionaries
        categories_data = []
        for cat in categories:
            # Generate the dictionary based on flags
            cat_dict = cat.to_dict(
                include_subcategories=include_subcategories,
                include_courses=is_courses_requested
            ) if include_subcategories else cat.to_dict()

            # 2. If courses are requested, filter their keys specifically
            if is_courses_requested and 'subcategories' in cat_dict:
                for sub in cat_dict['subcategories']:
                    if 'courses' in sub:
                        # FILTER LOGIC: Keep only specific keys
                        allowed_keys = {
                            'id', 'title', 'short_description', 
                            'duration_hours', 'price', 'thumbnail'
                        }
                        
                        sub['courses'] = [
                            {k: course[k] for k in allowed_keys if k in course}
                            for course in sub['courses']
                        ]
            
            categories_data.append(cat_dict)

        return jsonify({
            "message": "Master categories fetched successfully",
            "count": count,
            "categories": categories_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ GET all subcategories
"""Get All Subcategories with courses"""
@public_bp.route("/get-subcategories", methods=["POST"])
@limiter.limit("60 per minute")
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
@limiter.limit("60 per minute")
def get_subcategory(subcategory_id):
    try:
        subcategory = SubCategory.query.get_or_404(subcategory_id)
        return jsonify(subcategory.to_dict(include_courses=True)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@public_bp.route('/get-courses/<int:course_id>', methods=['POST'])
@limiter.limit("60 per minute")
def get_course(course_id):
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        # Parse query params
        include_lessons = request.args.get("lessons", "false").lower() == "true"
        include_resources = request.args.get("resources", "false").lower() == "true"
        limited_resources = request.args.get("limited_resources", "false").lower() == "true"

        # Check enrollment
        user = get_current_user()
        is_enrolled = False
        if user:
            enrollment = Enrollment.query.filter_by(
                user_id=user.id, course_id=course_id, is_active=True
            ).first()
            is_enrolled = enrollment is not None
        
        # Convert to dictionary
        # We must request resources initially to extract the first one
        should_fetch_resources = include_resources or limited_resources
        
        course_data = course.to_dict(
            include_modules=True, 
            include_lessons=include_lessons, 
            include_resources=should_fetch_resources
        )
        
        modules = course_data.get('modules', [])
        
        # --- LOGIC: Extract First Resource ---
        if limited_resources and modules:
            first_module = modules[0]
            lessons = first_module.get('lessons', [])
            if lessons:
                first_lesson = lessons[0]
                resources = first_lesson.get('resources', [])
                if resources:
                    # Add specific first resource to root
                    course_data['first_lesson_resource'] = resources[0]

        # --- LOGIC: Clean up Data ---
        for module in modules:
            for lesson in module.get('lessons', []):
                # 1. Remove video_url if not enrolled
                if not is_enrolled:
                    lesson.pop('video_url', None)
                
                # 2. If limited_resources is ON, remove the 'resources' list from lessons
                #    (so we don't send the full list, just the one we extracted above)
                if limited_resources:
                     lesson.pop('resources', None)

        course_data['is_enrolled'] = is_enrolled
        
        return jsonify({'course': course_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@public_bp.route('/get-courses', methods=['POST'])
@limiter.limit("30 per minute")
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



@public_bp.route('/test-session')
def test_session():
    session['Test'] = "testing redis for managing sessions"
    session['pending_user'] = session.get('pending_user')
    return jsonify(session.get('pending_user'), session.get('Test'))

 