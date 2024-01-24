import cv2
import os


def generate_thumbnail(video_path, output_path, frame_number):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Set the frame position
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # Read the specified frame
    ret, frame = cap.read()

    if not ret:
        raise ValueError(
            f"Unable to read frame {frame_number} from the video.")

    # Save the frame as a thumbnai;
    base_name = os.path.splitext(os.path.basename(video_path))[0]

    thumbnail_path = f"{base_name}.jpeg"
    cv2.imwrite(thumbnail_path, frame)

    # Release the video capture object
    cap.release()

    return thumbnail_path


if __name__ == "__main__":
    # Replace 'input_video.mp4' with the path to your input video
    input_video_path = input("Enter the video path: ")

    # Replace 'output_thumbnail' with the desired output path and filename (without extension)
    output_thumbnail_path = 'test'

    # Specify the frame number for the thumbnail
    frame_number = 0  # Change this to the desired frame number

    # Call the function to generate a single thumbnail
    thumbnail_path = generate_thumbnail(
        input_video_path, output_thumbnail_path, frame_number)

    print(f"Thumbnail generated at: {thumbnail_path}")
