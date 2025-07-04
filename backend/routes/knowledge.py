import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from marshmallow import Schema, fields, ValidationError
import PyPDF2
from docx import Document
from services.bedrock_service import bedrock_service
from middleware.error_handler import handle_error, handle_validation_error

knowledge_bp = Blueprint('knowledge', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

class FileUploadSchema(Schema):
    category = fields.Str(missing='general')
    description = fields.Str(missing='', validate=lambda x: len(x) <= 500)

@knowledge_bp.route('/upload', methods=['POST'])
def upload_files():
    try:
        schema = FileUploadSchema()
        form_data = schema.load(request.form.to_dict())
        
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files uploaded'
            }), 400

        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            return jsonify({
                'success': False,
                'error': 'No files selected'
            }), 400

        if len(files) > 5:
            return jsonify({
                'success': False,
                'error': 'Maximum 5 files allowed'
            }), 400

        category = form_data['category']
        description = form_data['description']
        results = []

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        for file in files:
            if file and allowed_file(file.filename):
                try:
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    
                    file.save(file_path)
                    
                    if file.content_length and file.content_length > MAX_FILE_SIZE:
                        os.remove(file_path)
                        results.append({
                            'originalName': filename,
                            'error': 'File too large',
                            'status': 'failed'
                        })
                        continue

                    extracted_text = ''
                    if filename.lower().endswith('.pdf'):
                        extracted_text = extract_text_from_pdf(file_path)
                    elif filename.lower().endswith(('.doc', '.docx')):
                        extracted_text = extract_text_from_docx(file_path)

                    analysis = ''
                    if extracted_text.strip():
                        analysis = bedrock_service.analyze_document(extracted_text, filename)

                    file_record = {
                        'id': str(uuid.uuid4()),
                        'originalName': filename,
                        'filename': unique_filename,
                        'mimetype': file.content_type,
                        'size': os.path.getsize(file_path),
                        'category': category,
                        'description': description,
                        'extractedText': extracted_text[:10000],
                        'analysis': analysis,
                        'uploadDate': datetime.now().isoformat() + 'Z',
                        'status': 'processed'
                    }

                    results.append(file_record)
                    os.remove(file_path)

                except Exception as e:
                    print(f"Error processing file {filename}: {e}")
                    results.append({
                        'originalName': filename,
                        'error': f'Failed to process: {str(e)}',
                        'status': 'failed'
                    })
            else:
                results.append({
                    'originalName': file.filename,
                    'error': 'Invalid file type',
                    'status': 'failed'
                })

        successful_files = len([r for r in results if r.get('status') == 'processed'])
        
        return jsonify({
            'success': True,
            'data': {
                'files': results,
                'message': f'Successfully processed {successful_files} of {len(results)} files'
            }
        })

    except ValidationError as e:
        return handle_validation_error(e.messages)
    except Exception as e:
        print(f"File upload error: {e}")
        return handle_error('Failed to upload files. Please try again.', 500)

@knowledge_bp.route('/files', methods=['GET'])
def get_files():
    try:
        files = []
        
        return jsonify({
            'success': True,
            'data': {
                'files': files,
                'total': len(files)
            }
        })

    except Exception as e:
        print(f"Get files error: {e}")
        return handle_error('Failed to fetch files', 500)

@knowledge_bp.route('/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        })

    except Exception as e:
        print(f"Delete file error: {e}")
        return handle_error('Failed to delete file', 500)

@knowledge_bp.route('/search', methods=['GET'])
def search_files():
    try:
        query = request.args.get('query')
        category = request.args.get('category', '')

        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400

        results = []

        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'query': query,
                'category': category
            }
        })

    except Exception as e:
        print(f"Search files error: {e}")
        return handle_error('Failed to search files', 500)

@knowledge_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'Knowledge base service is healthy',
        'timestamp': datetime.now().isoformat() + 'Z'
    }) 