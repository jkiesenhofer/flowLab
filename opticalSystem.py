import cv2
from vmbpy import VmbSystem, FrameStatus

# --- CONFIGURATION ---
OUTPUT_FILENAME = 'allied_vision_output.mp4'
FRAME_WIDTH = 1920   # Match your camera's resolution
FRAME_HEIGHT = 1080  # Match your camera's resolution
FPS = 30.0          # Desired frames per second
RECORD_SECONDS = 5   # Duration of the video

def main():
    # 1. Initialize the Video Writer
    # 'mp4v' is widely compatible. You can also use 'XVID' or 'avc1'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(
        OUTPUT_FILENAME, 
        fourcc, 
        FPS, 
        (FRAME_WIDTH, FRAME_HEIGHT)
    )

    print("Initializing Vimba System...")
    with VmbSystem.get_instance() as vmb:
        # 2. Access the camera
        cams = vmb.get_all_cameras()
        if not cams:
            print("No Allied Vision cameras found.")
            return
        
        cam = cams[0] # Get the first available camera
        print(f"Connecting to camera: {cam.get_name()} ({cam.get_id()})")

        with cam:
            # 3. Setup camera features (Optional but recommended)
            # Try to set pixel format to BGR8 so it matches OpenCV directly
            try:
                cam.get_feature_by_name('PixelFormat').set('BGR8')
            except Exception:
                print("Could not set PixelFormat to BGR8. Using default.")

            print(f"Recording started. Saving to '{OUTPUT_FILENAME}'...")
            print("Press 'q' in the preview window to stop early.")

            frames_to_record = int(FPS * RECORD_SECONDS)
            frames_saved = 0

            # 4. Start streaming
            cam.start_streaming()

            try:
                while frames_saved < frames_to_record:
                    # Get a single frame from the camera (timeout in milliseconds)
                    frame = cam.get_frame(timeout_ms=2000)

                    # Verify the frame is valid and complete
                    if frame.get_status() == FrameStatus.Complete:
                        
                        # Convert the Vimba frame to a Numpy array for OpenCV
                        # VmbPy handles color conversion automatically if set to BGR8
                        img = frame.as_numpy_ndarray()

                        # If your camera doesn't support BGR8 native output, 
                        # you might need to convert it manually here:
                        # img = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2BGR) 

                        # Write the frame to the video file
                        video_writer.write(img)
                        frames_saved += 1

                        # Optional: Display the live preview
                        # Resize for preview if the camera resolution is too large
                        preview_img = cv2.resize(img, (800, 450)) 
                        cv2.imshow('Allied Vision Live Preview', preview_img)

                        # Break loop if 'q' is pressed
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            print("Recording stopped early by user.")
                            break
                    else:
                        print("Incomplete frame dropped.")

            finally:
                # 5. Clean up and release resources
                cam.stop_streaming()
                video_writer.release()
                cv2.destroyAllWindows()
                print(f"Recording finished. Total frames saved: {frames_saved}")

if __name__ == '__main__':
    main()
