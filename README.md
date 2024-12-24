# Video Streaming Application

This is a FastAPI-based application for streaming videos from an AWS S3 bucket. The application allows users to upload, list, and stream videos.

## Features

- List videos stored in an S3 bucket
- Stream videos with support for HTTP range requests
- Upload videos to the S3 bucket using multipart upload

## Requirements

- Python 3.7+
- AWS account with S3 bucket
- AWS credentials configured

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/videostreaming.git
   cd videostreaming

2. Create a virtual environment and activate it:
```python
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the dependencies:
```pip install -r requirements.txt```

4. Create a .env file in the root directory and add your AWS credentials and bucket name:

```AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_BUCKET_NAME=your_bucket_name
```

Usage
Run the FastAPI application:

```uvicorn main:app --reload```

Open your browser and navigate to http://127.0.0.1:8000 to access the application.

Endpoints
1. GET /: List all videos in the S3 bucket.
GET /videos/{video_name}: Stream a specific video.
2. GET /watch/{video_name}: Watch a specific video in a web page.
3. GET /upload: Display the upload form.
POST /upload: Upload a video to the S3 bucket.

Example

List Videos
Navigate to http://127.0.0.1:8000 to see a list of videos stored in the S3 bucket.

Stream Video

Navigate to http://127.0.0.1:8000/videos/{video_name} to stream a specific video. Replace {video_name} with the name of the video file.

Watch Video

Navigate to http://127.0.0.1:8000/watch/{video_name} to watch a specific video in a web page. Replace {video_name} with the name of the video file.

Upload Video

Navigate to http://127.0.0.1:8000/upload to display the upload form.
1. Fill in the title and select a video file to upload.
2. Click the upload button to upload the video to the S3 bucket.