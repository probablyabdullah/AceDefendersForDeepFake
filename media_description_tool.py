import time
import pprint
import google.generativeai as genai
from config import gemini_api_key as api_key

def process_video_and_generate_content(video_path, media_type="image"):
    # Configure the generative AI with the provided API key
    genai.configure(api_key=api_key)
    
    
    # Upload the video file
    print(f"Uploading file...")
    video_file = genai.upload_file(path=video_path)
    print(f"Completed upload: {video_file.uri}")
    
    # Wait for the video file to be processed
    while video_file.state.name == "PROCESSING":
        print('Waiting for video to be processed.')
        time.sleep(10)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError("Video processing failed")
    print(f'Video processing complete: {video_file.uri}')

    # Use the Gemini model for content generation
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

    # Define safety settings
    safety_settings = [
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]

    # Create the prompt
    prompt = f"Create a description of events in the {media_type}. Identify the entities and people if present. Be as detailed as possible"
    
    # Make the LLM request
    print("Making LLM inference request...")
    response = model.generate_content([prompt, video_file], safety_settings=safety_settings)
    
    return response.text

# Example usage:
# process_video_and_generate_content("path/to/your/video.mp4", "your_api_key_here")
if __name__ == "__main__":
    # vedio_path=r"C:\Users\91787\Downloads\videoplayback (2).mp4"
    vedio_path = ""
    process_video_and_generate_content(vedio_path)

