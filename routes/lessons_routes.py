from models import Course,CourseModule,Lesson,UserRole
from flask import Blueprint,request,jsonify    
from app import db 
from auth import instructor_required
from auth import get_current_user
import os 
from dotenv import load_dotenv
from services.file_service import FileService
load_dotenv()

file_service = FileService()

lessons_bp = Blueprint("lessons_bp",__name__)

@lessons_bp.route("/")
def lessons():
    return {
        "page":"lessons",
        "status":"🆗"
    }


UPLOAD_FOLDER =  "lesson-videos"

ALLOWED_VIDEO_EXTENSIONS_LESSONS = {'mp4', 'avi', 'mov', 'mkv'}


#create lesson
"""Create a lesson """ 
@lessons_bp.route('/create-lessons/<int:module_id>', methods=['POST'])
@instructor_required
def create_lesson(module_id):
    try:
        module = CourseModule.query.get(module_id)
        data = request.get_data()

        if not module:
            return jsonify({'error': 'Course or module not found'}), 404

        # Handle form data (supports file + text)
        title = request.form.get('title')
        content = request.form.get('content')
        # duration_minutes = request.form.get('duration_minutes', type=int)
        is_preview = request.form.get('is_preview', 'false').lower() == 'true'
        video_file = request.files.get('video')
        
        duration_minutes = request.form.get("duration_minutes")

        print("title",title)

        if not title:
            return jsonify({'error': 'Lesson title is required'}), 400

        # Get next order number
        max_order = db.session.query(db.func.max(Lesson.order)).filter_by(module_id=module_id).scalar() or 0

        
        if file_service.validate_file_type(filename=video_file.filename,allowed_extensions=ALLOWED_VIDEO_EXTENSIONS_LESSONS):
            relative_path, file_size = file_service.save_file(file=video_file,subfolder=UPLOAD_FOLDER)
        else:
            return {
                "error":"file is not valid!"
            }
         
        
        lesson = Lesson(
            module_id=module_id,
            title=title,
            content=content,
            video_url=relative_path,
            duration_minutes=duration_minutes,
            order=max_order + 1,
            is_preview=is_preview
        )

        db.session.add(lesson)
        db.session.commit()

        return jsonify({
            'message': 'Lesson created successfully',
            'lesson_id': lesson.id,
            'lesson': lesson.to_dict(include_vedio=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


        

# get lessons 
"""Get lessons """
@lessons_bp.route('/get-lessons', methods=['POST'])
@instructor_required
def list_lessons_all():
    try:
        user = get_current_user()
        # include_vedio = request.args.get("include_vedio")
        # Role check
        if user.role != UserRole.INSTRUCTOR or user.role != UserRole.ADMIN:
            return jsonify({'error': 'Unauthorized to view lessons'}), 403

        lessons = Lesson.query.all()

        return jsonify({
            'lessons': [lesson.to_dict() for lesson in lessons]
        }), 200




    except Exception as e:
        return jsonify({'error': str(e)}), 500

# get lessons 
"""Get a specificlesson """
@lessons_bp.route('/get-lessons/<int:lesson_id>', methods=['POST'])
@instructor_required
def list_lessons(lesson_id):
    try:
        lessons = Lesson.query.get(lesson_id)

        if not lessons.is_preview:
            return jsonify({
            'lessons': lessons.to_dict(include_resources=True,include_vedio=False)
        }), 200
        else:
            return jsonify({
                'lessons': lessons.to_dict(include_resources=True)
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@lessons_bp.route('/update-lessons/<int:lesson_id>', methods=['PUT'])
@instructor_required
def update_lesson(lesson_id):
    try:
        print("lesson update route ---")
        lesson = Lesson.query.get(lesson_id)

        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404

        # ✅ Support both JSON and form-data (with optional file)
        data = request.form if request.form else request.get_json(silent=True) or {}
        
        print(type(data))
        
        print(data)

        # Update text fields
        if 'title' in data and data['title']:
            lesson.title = data['title']
        if 'content' in data:
            lesson.content = data['content']
        if 'duration_minutes' in data:
            lesson.duration_minutes = int(data['duration_minutes'])
        if 'is_preview' in data:
            lesson.is_preview = str(data['is_preview']).lower() == 'true'

        # ✅ Handle video update (optional)
        video_file = request.files.get('video')
        print("vedio from request:",video_file)
        if video_file and file_service.validate_file_type(filename=video_file.filename,allowed_extensions= ALLOWED_VIDEO_EXTENSIONS_LESSONS):
            # Delete old file if exists
            if lesson.video_url and os.path.exists(lesson.video_url):
                try:
                    file_service.delete_file(lesson.video_url)                
                except Exception as e:
                    print(f"Warning: could not delete old video: {e}")

            relative_path, file_size = file_service.save_file(video_file,subfolder=UPLOAD_FOLDER)
            print(relative_path)
            lesson.video_url = relative_path

          
            # duration_minutes = file_service.get_video_duration_minutes(relative_path)

            # lesson.duration_minutes = duration_minutes

        # ✅ Commit updates
        db.session.commit()

        return jsonify({
            'message': 'Lesson updated successfully',
            'lesson': lesson.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# delete lesson 
""" Delete a Lesson   """
@lessons_bp.route('/delete-lessons/<int:lesson_id>', methods=['DELETE'])
@instructor_required
def delete_lesson(lesson_id):
    try:

        lesson = Lesson.query.get(lesson_id)

        file_service.delete_file(lesson.video_url)

        db.session.delete(lesson)
        db.session.commit()

        return jsonify({'message': 'Lesson deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


