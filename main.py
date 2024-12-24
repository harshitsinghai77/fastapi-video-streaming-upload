import os
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from dotenv import load_dotenv
import boto3
from botocore.exceptions import NoCredentialsError
import httpx
from datetime import datetime, UTC

load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

templates.env.globals.update(now=lambda: datetime.now(UTC))

# Initialize AWS S3 client
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

@app.get('/', response_class=HTMLResponse)
async def home(request: Request):
    try:
        response = s3_client.list_objects_v2(Bucket=AWS_BUCKET_NAME)
        videos = [{'name': obj['Key']} for obj in response.get('Contents', [])]
    except NoCredentialsError:
        videos = []
    return templates.TemplateResponse('home.html', {'request': request, 'videos': videos})

@app.get('/videos/{video_name}')
async def get_video(video_name: str):
    try:
        video_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': AWS_BUCKET_NAME, 'Key': video_name}, ExpiresIn=3600)
    except NoCredentialsError:
        return {'error': 'video not found'}
    
    async def video_stream():
        async with httpx.AsyncClient() as client:
            async with client.stream('GET', video_url, headers={'Range': 'bytes=0-'}, timeout=None) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
    return StreamingResponse(video_stream(), media_type='video/mp4')

@app.get('/watch/{video_name}', response_class=HTMLResponse)
async def watch_video(request: Request, video_name: str):
    title = video_name.rsplit('.', 1)[0].replace('_', ' ')
    return templates.TemplateResponse('watch.html', {'request': request, 'video_name': video_name, 'title': title})

@app.get('/upload', response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse('upload.html', {'request': request})

@app.post('/upload')
async def upload_video(request: Request, title: str = Form(...), video_file: UploadFile = File(...)):
    contents = await video_file.read()
    
    file_extension = video_file.filename.split('.')[-1]
    file_name = f"{title.replace(' ', '_')}.{file_extension}"
    try:
        # Initiate multipart upload
        multipart_upload = s3_client.create_multipart_upload(Bucket=AWS_BUCKET_NAME, Key=file_name)
        upload_id = multipart_upload['UploadId']
        
        # Upload parts
        part_size = 5 * 1024 * 1024  # 5 MB
        parts = []
        for i in range(0, len(contents), part_size):
            part_number = i // part_size + 1
            part = s3_client.upload_part(
                Bucket=AWS_BUCKET_NAME,
                Key=file_name,
                PartNumber=part_number,
                UploadId=upload_id,
                Body=contents[i:i + part_size]
            )
            parts.append({'PartNumber': part_number, 'ETag': part['ETag']})
        
        # Complete multipart upload
        s3_client.complete_multipart_upload(
            Bucket=AWS_BUCKET_NAME,
            Key=file_name,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        message = 'Video uploaded successfully.'
    except NoCredentialsError:
        message = 'Error uploading video.'
        
    return templates.TemplateResponse('upload.html', {'request': request, 'message': message})
