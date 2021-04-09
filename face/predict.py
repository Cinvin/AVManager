import os
from io import BytesIO
import PIL
import face_recognition
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import joblib


def predictimage(predict_image: bytes):
    im = PIL.Image.open(BytesIO(predict_image))
    im = im.convert('RGB')
    pilim = np.array(im)
    path = os.getcwd() + '/face/traindata/predict3094.clf'
    if os.path.exists(path):
        clf = joblib.load(path)

        # Find all the faces in the test image using the default HOG-based model
        face_locations = face_recognition.face_locations(pilim)
        no = len(face_locations)
        if no == 0:
            return [], []
        face_encodings = face_recognition.face_encodings(pilim, num_jitters=10, model="large")
        names = []
        for i in range(no):
            test_image_enc = face_encodings[i]
            name = clf.predict([test_image_enc])
            names.append(name[0])
        return names, face_locations
    return [], []


def draw_prediction_labels_on_image(img_data, predictions):
    """
    Shows the face recognition results visually.
    :param img_path: path to image to be recognized
    :param predictions: results of the predict function
    :return:
    """
    pil_image = Image.open(BytesIO(img_data)).convert("RGB")
    draw = ImageDraw.Draw(pil_image)

    for name, (top, right, bottom, left) in predictions:
        # Draw a box around the face using the Pillow module
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 243, 255), width=2)

        # There's a bug in Pillow where it blows up with non-UTF-8 text
        # when using the default bitmap font
        font = ImageFont.truetype("PingFang", 20, encoding="unic")
        text_width, text_height = draw.textsize(name.encode("UTF-8"))
        draw.text((left + 6, bottom - 5), name, fill=(0, 243, 255), font=font)

    # Remove the drawing library from memory as per the Pillow docs
    del draw

    # Display the resulting image
    imgByteArr = BytesIO()
    pil_image.save(imgByteArr, format='JPEG')
    return imgByteArr.getvalue()
