from models import LessonResource,CourseModule,Lesson,Course
from flask import Blueprint,request,jsonify
from app import db 
from auth import instructor_required
from flask_jwt_extended import get_current_user
from werkzeug.utils import secure_filename
import os 
from dotenv import load_dotenv
from services.file_service import FileService
from datetime import datetime
load_dotenv()

file_service = FileService()

lessons_resource_bp=Blueprint("lessons_resource_bp",__name__)

UPLOAD_FOLDER = "lesson-resources" 
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif", "mp4", "mp3", "wav", "avi", "mov", "docx", "pptx"}



@lessons_resource_bp.route("/")
def lessons():
    return {
        "page":"lesson resources",
        "status":"🆗"
    }





# -------------------------------
# Create a Lesson Resource with File Upload
# -------------------------------
@lessons_resource_bp.route("/create-lesson-resources/<int:lesson_id>", methods=["POST"])
def create_lesson_resource(lesson_id):   
    try:
        # 1️⃣ Extract fields
        title = request.form.get("title")

        if not lesson_id or not title:
            return jsonify({"error": "lesson_id and title are required"}), 400

        # 2️⃣ Fetch lesson, module, and course
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return jsonify({"error": f"Lesson with id {lesson_id} not found"}), 404

        module = CourseModule.query.get(lesson.module_id)
        if not module:
            return jsonify({"error": f"Module for lesson {lesson_id} not found"}), 404

        course = Course.query.get(module.course_id)
        if not course:
            return jsonify({"error": f"Course for module {module.id} not found"}), 404

        # 3️⃣ Handle file upload
        if "file" not in request.files:
            return jsonify({"error": "File is required"}), 400

        file = request.files["file"]
        
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not file_service.validate_file_type(file.filename,allowed_extensions=ALLOWED_EXTENSIONS):
            return jsonify({"error": "File type not allowed"}), 400

        relative_path, file_size = file_service.save_file(file,subfolder=UPLOAD_FOLDER)

      
        # 6️⃣ Create DB entry
        resource = LessonResource(
            lesson_id=lesson.id,
            title=title,
            file_path=relative_path,
            file_type=file_service.get_file_extension(file.filename),
            file_size=file_size,
            created_at=datetime.utcnow()
        )

        db.session.add(resource) 
        db.session.commit()
    
        # Optional: Include course/module details in response
        response_data = resource.to_dict()
        response_data.update({
            "message":"lesson resource updated successfully!",
            "lesson_title": lesson.title,
            "module_title": module.title,
            "course_title": course.title
        })

        return jsonify(response_data), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500




# -------------------------------
# READ ALL (GET)
# -------------------------------
@lessons_resource_bp.route("/get-lesson-resources", methods=["POST"])
def get_all_resources():
    try:
        resources = LessonResource.query.all()
        return jsonify([res.to_dict() for res in resources]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ------------------------------- 
# READ SINGLE (GET by ID)
# -------------------------------
@lessons_resource_bp.route("/get-lesson-resources/<int:resource_id>", methods=["POST"])
def get_resource(resource_id):
    resource = LessonResource.query.get(resource_id)
    if not resource:
        # return jsonify({"error": "Resource not found"}), 404
        return  file_service.send_file(resource.file_path)
    return jsonify(resource.to_dict()), 200




# -------------------------------
# UPDATE (PUT) with file replacement
# -------------------------------
@lessons_resource_bp.route("/update-lesson-resources/<int:resource_id>", methods=["PUT"])
def update_resource(resource_id):
    try:
        resource = LessonResource.query.get(resource_id)
        if not resource:
            return jsonify({"error": "Resource not found"}), 404

        title = request.form.get("title", resource.title)
        resource.title = title
        resource.lesson_id = request.form.get("lesson_id", resource.lesson_id)

        # Handle file update if a new one is uploaded
        if "file" in request.files:
            file = request.files["file"]
            print("file:",file)
            if file_service.validate_file_type(file.filename,ALLOWED_EXTENSIONS):
                file_service.delete_file(resource.file_path)

            relative_path, file_size = file_service.save_file(file,UPLOAD_FOLDER)
            resource.file_path = relative_path
            resource.file_type = file_service.get_file_extension(file.filename)
            resource.file_size = file_size

        db.session.commit()
        return jsonify(resource.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# -------------------------------
# DELETE (remove from DB + file)
# -------------------------------

@lessons_resource_bp.route("/delete-lesson-resources/<int:resource_id>", methods=["DELETE"])
def delete_resource(resource_id):
    try:
        resource = LessonResource.query.get(resource_id)
        if not resource:
            return jsonify({"error": "Resource not found"}), 404

        # Delete file from disk
        if resource.file_path and os.path.exists(resource.file_path):
            file_service.delete_file(resource.resource.file_path)

        db.session.delete(resource)
        db.session.commit()

        return jsonify({"message": "Resource deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


