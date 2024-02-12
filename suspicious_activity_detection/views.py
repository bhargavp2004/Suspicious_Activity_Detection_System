# views.py

from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Video
from .forms import VideoForm
from collections import deque
from tensorflow.keras.models import load_model
from django.conf import settings
import numpy as np
import os
import cv2
from pathlib import Path

IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
SEQUENCE_LENGTH = 30
CLASSES_LIST = ["Explosion", "fights", "NormalVideos", "Shooting", "Stealing"]
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

def load_trained_model():
    model_path = r'D:\B.TECH\6TH SEMESTER\Machine Learning\Project\Suspicious Activity Detection\Suspicious_Activity_Detection_ProjectML\Suspicious_Human_Activity_Detection.h5'
    model = load_model(model_path)
    print("Model Loaded Successfully!")
    return model

def predict_on_video(model, video_file_path):
    video_reader = cv2.VideoCapture(video_file_path)
    original_video_width = int(video_reader.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_video_height = int(video_reader.get(cv2.CAP_PROP_FRAME_HEIGHT))

    output_file_path_relative = os.path.join(
        'output_videos',
        f"{os.path.basename(video_file_path)}"
    )
    output_file_path_relative = output_file_path_relative.replace('\\', '/')

    output_file_path = os.path.join(MEDIA_ROOT, output_file_path_relative)

    video_writer = cv2.VideoWriter(output_file_path, cv2.VideoWriter_fourcc(*'H264'), video_reader.get(cv2.CAP_PROP_FPS), (original_video_width, original_video_height))

    frames_queue = deque(maxlen=SEQUENCE_LENGTH)

    predicted_class_name = ''
    while video_reader.isOpened():
        ok, frame = video_reader.read()

        if not ok:
            print('break')
            break
        resized_frame = cv2.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH))
        normalized_frame = resized_frame / 255

        frames_queue.append(normalized_frame)
        if len(frames_queue) == SEQUENCE_LENGTH:
            predicted_labels_probabilities = model.predict(np.expand_dims(frames_queue, axis=0))[0]
            predicted_label = np.argmax(predicted_labels_probabilities)
            predicted_class_name = CLASSES_LIST[predicted_label]

        cv2.putText(frame, predicted_class_name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        video_writer.write(frame)

    video_reader.release()
    video_writer.release()
    return output_file_path_relative

def handle_uploaded_video(video_file):
    destination_path = os.path.join(
        MEDIA_ROOT,
        'uploaded_videos',
        video_file.name
    )
    with open(destination_path, 'wb+') as destination:
        for chunk in video_file.chunks():
            destination.write(chunk)

    return destination_path

def predict_and_save_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            model = load_trained_model()
            video_file = request.FILES['video_file']
            video_path = handle_uploaded_video(video_file)

            # Predict on the uploaded video
            output_file_path_relative = predict_on_video(model, video_path)
            org_out_path = output_file_path_relative
            print("Before: ", org_out_path)

            # Constructing the full absolute path
           # Constructing the full absolute path
            output_file_path = os.path.join(settings.MEDIA_ROOT, output_file_path_relative)
            output_file_path = output_file_path.replace('\\', '/')  # Assigning the modified path back to the variable
            print("After: ", output_file_path)

            video_file = video_file
            output_file = output_file_path_relative
            output_file = output_file.replace('\\', '/')  # Corrected assignment here
            context = {'videofile': org_out_path, 'actualfile': video_path}

            return render(request, 'result.html', context=context)
    else:
        form = VideoForm()

    return render(request, 'upload_video.html', {'form': form})

def index(request):
    return render(request, 'index.html')



    