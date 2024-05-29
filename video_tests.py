from skimage.feature import hog
import os, cv2, datetime, json
import keras.backend as K
import numpy as np
K.clear_session()

from facial_emotions import inferencia

class VideoAnalysis:
    """
        Purpose: Carry out emotion analysis
        Methods: preprocess_input, video_emotion
    """
    def __init__(self):
        """
            :param self:
            :param video_path: Path where video file would be downloaded
            :return: No output
            Purpose: Constructor of class
        """
        self.video_path = "facial_emotions/video/"
        self.graph_path = "facial_emotions/graph_generated/"
        self.json_path = "facial_emotions/json_files/"
        
        self.input_shape = (48, 48, 1)
        self.weights_1 = 'facial_emotions/saved_models/vggnet.h5'
        self.weights_2 = 'facial_emotions/saved_models/vggnet_up.h5'

        self.model_1 = inferencia.VGGNet(self.input_shape, 7, self.weights_1)
        self.model_1.load_weights(self.model_1.checkpoint_path)

    def get_landmarks(self, image, rects):
        return np.matrix([[p.x, p.y] for p in self.predictor(image, rects[0]).parts()])

    def sliding_hog_windows(self, image):
        hog_windows = []
        for y in range(0, self.height, self.window_step):
            for x in range(0, self.width, self.window_step):
                window = image[y:y+self.window_size, x:x+self.window_size]
                hog_windows.extend(hog(window, orientations=8, pixels_per_cell=(8, 8),
                                                cells_per_block=(1, 1)))
        return hog_windows

    def video_smile(self, video_name, emo_id, db):
        # If opencv is able to read video file
        try:
            cap = cv2.VideoCapture(os.path.join(self.video_path, video_name))
        except cv2.error as e:
            return e

        smilesSum=0

        # Initialize dict for emotions and seconds
        seconds=[]
        smiles=[]

        # json file for writing emotions and their percentages
        path = self.json_path + video_name + '.json'
        json_file = open(path, 'w')

        # count the number of frames
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = cap.get(cv2.CAP_PROP_FPS)

        #If fps not fetched initialize fps
        if fps > 100:
           fps = 25

        # Initializing variables for fps rate
        fps_skip=0
        sec=0
        fps=np.round(fps)
        
        # Loop until video is running
        while (cap.isOpened()):
            try:
                # Read frame
                ret, frame = cap.read()
                
                # skipping to certain frame for fps_rate
                cap.set(cv2.CAP_PROP_POS_FRAMES, fps_skip)
                
                fps_skip += fps
                fps_skip=np.round(fps_skip)

                if not (ret) or fps_skip>=frames:
                    break

                smile, smile_prob = self.model_1.infer_single_image(frame, self.model_1)
                
                if smile=="Happy" and round(smile_prob*100, 2)>85:
                    smilesSum+=1
                    smiles.append(round(smile_prob*100, 2))
                else:
                    smiles.append(0)

                seconds.append(sec)
                sec+=1

            except Exception as e:
                print("Exception: ",e)
                continue
        
        sum4p = (np.round(smilesSum,3) / sec)*100
        
        emo_prob = { 
            "status_code": 200,
            "status_message": "SUCCESS",
            "Emotion_Src": str(emo_id),
            "GraphTime": str(seconds)[1:-1],
            "Emotions":{
                "Positivo": str(smiles)[1:-1],
            },
            "Percentages": {
                "Smiles": str(np.round(sum4p,2)),
            },
            "Duration": str(datetime.timedelta(seconds=sec)),
            "Seconds": str(sec),
        }

        json_file.write(json.dumps(emo_prob))

        # Destroy All open windows of opencv
        cv2.destroyAllWindows()
        # Release the VIDEO
        cap.release()
        
        json_file.close()

        with open(path, "r") as json_file:
            json_data = json_file.read()  

        _=db.updateStatus(4, emo_id)
        _=db.updateData(json_data, emo_id)
        
        return emo_prob
           