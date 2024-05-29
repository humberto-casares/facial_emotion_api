from datetime import datetime
import threading
import video_tests
from database import Database  # Ensure this import is aligned with your actual file structure

# Database configuration
db_config = {
    "host": "68.183.49.100",
    "user": "rolplay_emotions",
    "password": "k!TsEMU1X6$EG4FQ8be8$c",
    "database": "rolplay_emotions"
}

video_p = video_tests.VideoAnalysis()

def video_process(emotion_src, results, index, db_config):
    db = Database(**db_config)
    # Extracting video name from database with ID emotion_src
    file_name = db.getStatusMedia(emotion_src)

    # If ID does not exist, endpoint stops here
    if file_name is None:
        results[index] = {"status_code": 404, "status_message": "id-not-found"}
        return
    try:
        # Starting processing initial time
        start = datetime.now()

        try:
            analitics = video_p.video_smile(file_name, emotion_src, db)
        except Exception as e:
            results[index] = {"status_code": 500, "status_message": "Processing Error: " + str(e)}
            return

        # End of processing to store the amount of time that it took
        end = datetime.now()

        analitics["Start_Time_Facial"] = start  # Adding this value to json
        analitics["End_Time_Facial"] = end  # Adding this value to json
        analitics["Processing_Time_Facial"] = end - start  # Adding this value to json

        results[index] = analitics
    except Exception as e:
        results[index] = {"status_code": 500, "status_message": "Internal Server Error: " + str(e)}

# List of emotion sources to process
emotion_sources = ["c77bKrw60D12Wt", "O3LE4JcHswherf", "6Wf4gB010zTOH9", "99K5ex4mx", "99K5ex4mx34"]

# Placeholder for results
results = [None] * len(emotion_sources)

# List to keep track of threads
threads = []

# Creating and starting threads
for index, src in enumerate(emotion_sources):
    thread = threading.Thread(target=video_process, args=(src, results, index, db_config))
    threads.append(thread)
    thread.start()

# Joining threads to ensure all are completed
for thread in threads:
    thread.join()

# Printing results
for index, res in enumerate(results):
    print(f"\nRes for {emotion_sources[index]}: {res}")
