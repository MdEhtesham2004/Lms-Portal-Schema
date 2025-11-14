from models import MasterCategory,Course,SubCategory,CourseStatus
from flask import Blueprint,request,jsonify    
from app import db 
from auth import admin_required


subcategory_bp = Blueprint("subcategory_bp",__name__)


@subcategory_bp.route("/")
def subcategories():
    return {
        "page":"subcategories",
        "status":"🆗"
    }



# Create SubCategory only
"""Create subCategories """
@admin_required
@subcategory_bp.route("/create-subcategories", methods=["POST"])
def create_only_subcategory():
    try:
        data = request.get_json()

        # Validate required fields
        if "master_category_id" not in data:
            return jsonify({"error": "master_category_id is required"}), 400
        if "name" not in data or not data["name"].strip():
            return jsonify({"error": "SubCategory name is required"}), 400

        # Check if master category exists
        master = MasterCategory.query.get(data["master_category_id"])
        if not master:
            return jsonify({"error": "MasterCategory not found"}), 404

        # Create SubCategory
        subcategory = SubCategory(
            name=data["name"].strip(),
            master_category_id=master.id
        )   
        db.session.add(subcategory)
        db.session.commit()

        return jsonify({
            "message": "SubCategory created successfully",
            "subcategory": subcategory.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# ✅ GET all subcategories
"""Get All Subcategories with courses"""
@admin_required
@subcategory_bp.route("/get-subcategories", methods=["POST"])
def get_all_subcategories():
    try:
        include_courses=request.args.get("courses")
        subcategories = SubCategory.query.all()
        return jsonify([sub.to_dict(include_courses=True)  if include_courses is not None else sub.to_dict() for sub in subcategories]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ✅ GET single subcategory by ID
""" GET single subcategory by ID"""
@admin_required
@subcategory_bp.route("/get-subcategories/<int:subcategory_id>", methods=["POST"])
def get_subcategory(subcategory_id):
    try:
        subcategory = SubCategory.query.get_or_404(subcategory_id)
        return jsonify(subcategory.to_dict(include_courses=True)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ✅ UPDATE subcategory
"""Update Category with specific id """
@admin_required
@subcategory_bp.route("/update-subcategories/<int:subcategory_id>", methods=["PUT"])
def update_subcategory(subcategory_id):
    try:
        data = request.get_json()
        subcategory = SubCategory.query.get_or_404(subcategory_id)

        # Update name if provided
        if "name" in data and data["name"].strip():
            subcategory.name = data["name"].strip()

        # Update master_category_id if provided
        if "master_category_id" in data:
            master = MasterCategory.query.get(data["master_category_id"])
            if not master:
                return jsonify({"error": "MasterCategory not found"}), 404
            subcategory.master_category_id = master.id

        db.session.commit()
        return jsonify({
            "message": "SubCategory updated successfully",
            "subcategory": subcategory.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400



# ✅ DELETE subcategory
"""Delete Subcategory"""
@admin_required
@subcategory_bp.route("/delete-subcategories/<int:subcategory_id>", methods=["DELETE"])
def delete_subcategory(subcategory_id):
    try:
        subcategory = SubCategory.query.get_or_404(subcategory_id)
        db.session.delete(subcategory)
        db.session.commit()
        return jsonify({"message": "SubCategory deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400





