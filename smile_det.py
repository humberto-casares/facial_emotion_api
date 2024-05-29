import cv2

# Load the smile cascade
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_smiles(image_path, scale_factor=1.0):
    # Read the image
    image = cv2.imread(image_path)
    
    # Check if the image was successfully loaded
    if image is None:
        print("Error: Image not found or unable to load.")
        return
    
    # Resize the image if scale_factor is different than 1
    if scale_factor != 1.0:
        width = int(image.shape[1] * scale_factor)
        height = int(image.shape[0] * scale_factor)
        image = cv2.resize(image, (width, height))

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Initialize variable to check for happy smile
    happy_smile_detected = False

    # Loop over each face and detect smiles within the face region
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        smiles = smile_cascade.detectMultiScale(
            roi_gray,
            scaleFactor=1.8,
            minNeighbors=20,
            minSize=(25, 25),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # Consider a smile as happy if its width is more than half the width of the face
        for (sx, sy, sw, sh) in smiles:
            if sw > 0.5 * w:
                cv2.rectangle(image, (x+sx, y+sy), (x+sx+sw, y+sy+sh), (255, 0, 0), 2)
                happy_smile_detected = True

    # Determine the message to print on the image and console
    if happy_smile_detected:
        message = "Happy smile detected."
    else:
        message = "No happy smile detected."

    # Print message on the image
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, message, (10, 30), font, 1, (255, 0, 0), 2, cv2.LINE_AA)

    # Display the output
    cv2.imshow('Happy Smile Detection', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Print message to the console
    print(message)

    # Return smile presence as boolean
    return happy_smile_detected


detect_smiles("facial_emotions/images/pos.jpg",  scale_factor=0.2)
