from models import MasterCategory,Course,SubCategory,CourseStatus
from flask import Blueprint,request,jsonify    
from app import db 
from auth import admin_required



master_bp = Blueprint("master_bp",__name__)


@master_bp.route("/")
def mastercategories():
    return {
        "page":"mastercategories",
        "status":"🆗"
    }

"""Create only master categories"""
# Create MasterCategory only
@admin_required
@master_bp.route("/create-mastercategories", methods=["POST"])
def create_only_master_category():
    try:
        data = request.get_json()

        # Validate required field
        if "name" not in data or not data["name"].strip():
            return jsonify({"error": "Category name is required"}), 400

        # Create MasterCategory
        master = MasterCategory(name=data["name"].strip())
        db.session.add(master)
        db.session.commit()

        return jsonify({
            "message": "MasterCategory created successfully",
            "category": master.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

"""Get master Categories only"""
@admin_required
@master_bp.route('/get-mastercategories', methods=['POST'])
def get_master_categories_only():   
    try:
        include_subcategories=request.args.get("subcategories")
        include_courses=request.args.get("courses")
        
        if include_courses is not None and include_courses == "true":
            include_courses=True
        else:
            include_courses=False

        categories = MasterCategory.query.all()
        count = len(categories)
        
        categories = [
            cat.to_dict(include_subcategories=include_subcategories,include_courses=include_courses)
            if include_subcategories is not None else cat.to_dict()
            for cat in categories
        ]

        return jsonify({
            "message": "Master categories fetched successfully",
            "count": count,
            "mastercategories":categories
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""Update MasterCategory"""
@admin_required
@master_bp.route('/update-mastercategories/<int:id>', methods=['PUT'])
def update_master_category_only(id):
    try:
        data = request.get_json()

        # Validate input
        if "name" not in data or not data["name"].strip():
            return jsonify({"error": "Category name is required"}), 400

        category = MasterCategory.query.get(id)
        if not category:
            return jsonify({"error": "MasterCategory not found"}), 404

        category.name = data["name"].strip()
        db.session.commit()

        return jsonify({
            "message": "MasterCategory updated successfully",
            "category": category.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


"""Delete MasterCategory"""
@admin_required
@master_bp.route('/delete-mastercategories/<int:id>', methods=['DELETE'])
def delete_master_category_only(id):
    try:
        category = MasterCategory.query.get(id)
        if not category:
            return jsonify({"error": "MasterCategory not found"}), 404

        db.session.delete(category)
        db.session.commit()

        return jsonify({
            "message": "MasterCategory deleted successfully",
            "deleted_id": id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


"""Get all the Master Course with specific id including subcategories """
@admin_required
@master_bp.route("/get-mastercategories/<int:category_id>", methods=["POST"])
def get_master_category(category_id):
    try:
        category = MasterCategory.query.get_or_404(category_id)
        
        include_courses = request.args.get("courses", "false").lower() == "true"  # parse bool safely

        return jsonify(category.to_dict(include_subcategories=True,include_courses=include_courses)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400





