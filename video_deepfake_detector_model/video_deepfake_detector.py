import cv2
import numpy as np
from tensorflow.keras.models import load_model
from collections import Counter

model = load_model('files/vit_classifier_model (1).h5')

def video_deepfake_detector(url: str):
    return predict(url, "real")

def preprocess_image(image):
    """
    Preprocess the image for model prediction.

    Args:
    image (numpy array): Input image.

    Returns:
    numpy array: Preprocessed image.
    """
    # Resize the image to the required size
    resized_image = cv2.resize(image, (72, 72))
    # Normalize the image
    normalized_image = resized_image.astype('float32') / 255.0
    # Standardize the image
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    standardized_image = (normalized_image - mean) / std
    # Expand dimensions to match model input shape
    preprocessed_image = np.expand_dims(standardized_image, axis=0)
    return preprocessed_image

def predict(video_path, true_label):
    cap = cv2.VideoCapture(video_path)
    frame_predictions = []
    prediction_probabilities = []
    frame_count = 0  # To track the frame count

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        processed_frame = preprocess_image(frame)
        prediction = model.predict(processed_frame)
        predicted_class = int(prediction[0][0] > 0.5)
        frame_predictions.append(predicted_class)
        prediction_probabilities.append(prediction[0][0])
        frame_count += 1

    cap.release()

    if not frame_predictions:
        print("No frames were processed, unable to make a prediction.")
        return

    # Generate true_labels list with the same length as the number of frames
    true_labels = [true_label] * frame_count

    prediction_counts = Counter(frame_predictions)
    final_prediction = prediction_counts.most_common(1)[0][0]
    avg_prediction_prob = np.mean(prediction_probabilities)
    confidence = avg_prediction_prob if final_prediction == 1 else 1 - avg_prediction_prob

    if final_prediction == 1:
        return {
            "real": 1 - avg_prediction_prob,
            "fake": avg_prediction_prob
        }
    else:
        return {
            "real": avg_prediction_prob,
            "fake": 1 - avg_prediction_prob
        }

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=jTWb-RIdN-I"
    video = pafy.new(url)
    best = video.getbest(preftype="mp4")
    print(video_deepfake_detector(best.url))
    # YouTube(url).streams.first().download()
    # url = YouTube(url)
    # stream = url.streams.get_highest_resolution()
    # stream.download(output_path="test.mp4")
    # print(video_deepfake_detector(url))
    # print(url)

