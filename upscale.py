import os
import cv2


def upscale_to_1080p(input_path):
    # Open the input video file
    cap = cv2.VideoCapture(input_path)

    # Get the original video's frame width and height
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Extract the base name of the input file (excluding the extension)
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    # Create VideoWriter object for 1080p resolution
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_1080p_path = f'{base_name}_1080p.mp4'
    out_1080p = cv2.VideoWriter(output_1080p_path, fourcc, 30.0, (1920, 1080))

    while True:
        # Read a frame from the input video
        ret, frame = cap.read()

        # Break the loop if the video is finished
        if not ret:
            break

        # Resize the frame to 1080p and write to the 1080p output video
        frame_1080p = cv2.resize(frame, (1920, 1080))
        out_1080p.write(frame_1080p)

    # Release resources
    cap.release()
    out_1080p.release()

    print(f"Video upscale to 1080p complete. Output file: {output_1080p_path}")


if __name__ == "__main__":
    video = input("Enter video path to be upscaled")
    upscale_to_1080p(video)
