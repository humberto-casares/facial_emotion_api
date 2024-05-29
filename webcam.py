from facial_emotions import inferencia
import cv2

# Starting webcam
webcam = cv2.VideoCapture(0)

input_shape = (48, 48, 1)
weights_1 = 'facial_emotions/saved_models/vggnet.h5'

model_1 = inferencia.VGGNet(input_shape, 7, weights_1)
model_1.load_weights(model_1.checkpoint_path)

while True:
    # We get a new frame from the webcam
    ret, frame = webcam.read()

    smile, smile_prob = model_1.infer_single_image(frame, model_1)

    if smile=="Happy" and round(smile_prob*100, 2)>85:
        smiles = round(smile_prob*100, 2)
    else:
        smiles = 0
        
    # Put the text on the frame
    text = f"Smile: {smiles}%"
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the frame
    cv2.imshow('Webcam', frame)

    if cv2.waitKey(1) == 27:
        break

# cleanup the camera and close any open windows
webcam.release()
cv2.destroyAllWindows()