from fastapi.middleware.cors import CORSMiddleware
from validators import ValidationFailure
import wget, os, validators, random, string
from datetime import datetime
from fastapi import FastAPI
import video_tests
from database import Database

# Database configuration
db_config = {
    "host": "127.0.0.1",
    "user": "facial_emotions",
    "password": "a4vct4!3fas4%$ads",
    "database": "facial_emotions"
}

video_p = video_tests.VideoAnalysis()
db = Database(**db_config)

app = FastAPI()

# Configure CORS
origins = [
    "https://rolplay.net",
    "https://rolplaybeta.com.mx",
    "https://accelerationpluspitch.ca",
    "https://improveyourpitch.net",
    "https://improveyourpitchbeta.net",
    "https://talentoweb.com.mx"
    # Add any additional allowed origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

tags_metadata = [
    {
        "name": "create_job",
        "description": "With video URL, creates a register of the video to analyze and generates emotion_src.",
        "externalDocs": {
            "url": "http://68.183.49.100:8009/create_job?urlName=",
        },
    },
    {
        "name": "process_job_smiles",
        "description": "With the emotion_src, fetches mp4 file and processes presence of smiles and hands, returns json.",
        "externalDocs": {
            "url": "http://68.183.49.100:8009/process_job_smiles_hands?emotion_src=",
        },
    },
    {
        "name": "job_status",
        "description": "With the emotion_src, gets register status (1,2,3,4)",
        "externalDocs": {
            "url": "http://68.183.49.100:8009/job_status?emotion_src=",
        },
    },
    {
        "name": "job_data",
        "description": "With the emotion_src, gets register processing data",
        "externalDocs": {
            "url": "http://68.183.49.100:8009/job_data?emotion_src=",
        },
    },
    {
        "name": "delete_vid",
        "description": "With the mp4 file emotion_src, when analitics finish, deletes mp4 file in server",
        "externalDocs": {
            "url": "http://68.183.49.100:8009/delete_vid?emotion_src=",
        },
    },
]

app = FastAPI(
    title="RolPlay Facial Emotions",
    description="RolPlay API for Facial Emotion Classification with VGG Net",
    openapi_tags=tags_metadata,
)

@app.get("/")
def home():
    return {"RolPlay Facial Emotion API": "Welcome to Rolplay AI API for Facial Emotion Classification"}

# Se crea 
@app.post("/create_job", tags=["create_job"])
def create_job(urlName: str): 
    result = validators.url(urlName)
    if isinstance(result, ValidationFailure):
        return {"status_code": 400, "status_message": "Invalid URL"}

    # Extract URL filename
    filename = os.path.basename(urlName)
    # Allowed extensions for video processing with tensorflow
    allowed_extensions = [".mp4",'.mov','.MOV']
    _, extension = os.path.splitext(filename)
    
    if extension not in allowed_extensions:
        return {"status_code": 400, "status_message": "Invalid file extension"}
    
    try:
        # Downloading file from url and storing in folder out
        _ = wget.download(urlName, out='facial_emotions/video/')
    except Exception as e:
        return {"status_code": 404,"status_message": "URL not found: " + str(e)}

    # Adding stp_id to Database and generate emotion_src for relational database
    emotion_src = ''.join(random.sample(string.ascii_letters + string.digits, 14))

    bdIn = db.insertDB(emotion_src,filename,"",1,datetime.now())       
    
    if bdIn == 1:
        return {"status_code": 200,"status_message": "SUCCESS", "emotion_src": emotion_src}
    else:
        return {"status_code": 424,"status_message": "Insert Error"}

@app.post("/process_job_smiles", tags=["process_job_smiles"])
def process_job_smiles(emotion_src: str): 
    # Extracting video name from database with ID emotion_src
    file_name=db.getStatusMedia(emotion_src)

    # If ID does not exist, endpoint stops here
    if file_name == None:
        return {"status_code": 404,"status_message": "id-not-found"}
    try:
        # Starting processing initial time
        start=datetime.now()

        try:
            analitics = video_p.video_smile(file_name, emotion_src, db)
        except Exception as e:
            return {"status_code": 500, "status_message": "Processing Error: "+str(e)}  

        # End of processing to store the amount of time that it took
        end=datetime.now()

        analitics["Start_Time_Facial"] = start #Adding this value to json
        analitics["End_Time_Facial"] = end #Adding this value to json
        analitics["Processing_Time_Facial"] = end - start #Adding this value to json
        
        return analitics
    except Exception as e:
        return {"status_code": 500,"status_message": "Internal Server Error: "+str(e)}

@app.get("/job_status", tags=["job_status"])
def job_status(emotion_src: str):   
    # Consulting video ID processing status
    status = db.getStatusID(emotion_src)

    # If ID does not exist, endpoint stops here
    if status == None:
        return {"status_code": 404,"status_message": "id-not-found"}
    # Else, it returns the status as response
    else:
        return {"status_code": 200,"status_message": "SUCCESS", "emotion_status": status}

@app.get("/job_data", tags=["job_data"])
def job_data(emotion_src: str):   
    # Consulting video ID processing data
    status = db.getStatusData(emotion_src)

    # If ID does not exist, endpoint stops here
    if status == None:
        return {"status_code": 404,"status_message": "id-not-found"}
    # Else, it returns the status as response
    else:
        return {"status_code": 200,"status_message": "SUCCESS", "emotion_data": status}

@app.delete("/delete_vid", tags=["delete_vid"])
def delete_vid(emotion_src: str): 
    # Extracting video name from database with ID emotion_src
    file_name = db.getStatusMedia(emotion_src)

    # If ID does not exist, endpoint stops here
    if file_name == None:
        return {"status_code": 404,"status_message": "id-not-found"}

    try:
        # Deleting video at video_path
        video_path="/home/facial_vgg/facial_emotions/video/"+file_name
        os.remove("/home/facial_vgg/facial_emotions/video/"+file_name)
        return {"status_code": 200,"status_message": "Video at "+video_path+" deleted from server."}
    except Exception as e:
        return {"status_code": 500,"status_message": "Internal Server Error: "+str(e)}

'''
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="68.183.49.100", port=8009)
'''
