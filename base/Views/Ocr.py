from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
from io import BytesIO
from PyPDF2 import PdfReader
from base.models import PatientDocument
from g4f.client import Client

@login_required
def extract_text(request):
    if request.method == 'POST' and request.FILES.get('pdf'):
        pdf_file = request.FILES['pdf']
        
        client = MongoClient('mongodb+srv://nagi:nagi@cluster0.ohv5gsc.mongodb.net/')  # Use your MongoDB connection string
        db = client['ASD']
        fs = GridFS(db)
        
        file_id = fs.put(pdf_file.read(), filename=pdf_file.name)
        
        document = PatientDocument.objects.create(user=request.user, file_gridfs_id=str(file_id))
        
        grid_fs_file = fs.get(file_id)
        pdf_buffer = BytesIO(grid_fs_file.read())
        
        reader = PdfReader(pdf_buffer)
        
        extracted_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        
        summary = generate_summary(extracted_text)
        
        document.file_content = extracted_text
        document.summary = summary
        document.save()
    
    documents = PatientDocument.objects.filter(user=request.user)
    
    return render(request, 'Ocr/upload_image.html', {'documents': documents})

@login_required
def download_file(request, document_id):
    document = get_object_or_404(PatientDocument, id=document_id, user=request.user)
    
    client = MongoClient('mongodb+srv://nagi:nagi@cluster0.ohv5gsc.mongodb.net/')  # Use your MongoDB connection string
    db = client['ASD']
    fs = GridFS(db)
    
    grid_fs_file = fs.get(ObjectId(document.file_gridfs_id))
    
    response = HttpResponse(grid_fs_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{grid_fs_file.filename}"'
    
    return response

@login_required
def delete_file(request, document_id):
    document = get_object_or_404(PatientDocument, id=document_id, user=request.user)
    
    client = MongoClient('mongodb+srv://nagi:nagi@cluster0.ohv5gsc.mongodb.net/')  # Use your MongoDB connection string
    db = client['ASD']
    fs = GridFS(db)
    
    fs.delete(ObjectId(document.file_gridfs_id))
    
    document.delete()
    
    return redirect('ocr')

def generate_summary(text):
    client = Client()
    user_content = f"""
        Note:
        1. Give me the summary of the following content.
        2. The Summary should be in language of english
        3. dont use japanese.
        4. The summary should be in 1-5 lines.
        Text:
        {text}
    """
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a useful AI to provide the summary of the given content in English."},
            {"role": "user", "content": user_content}
        ]
    )
    ai_response = chat_completion.choices[0].message.content or ""
    return ai_response
