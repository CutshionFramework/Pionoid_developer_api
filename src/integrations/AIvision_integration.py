import cv2
import torch

class AIVisionIntegration:
    def __init__(self):
        # Initialize YOLO model
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        
        # Check if CUDA is available and if so, use it
        if torch.cuda.is_available():
            self.model = self.model.to('cuda')
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)  # Adjust '0' to your camera ID
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set the width to 640 pixels
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set the height to 480 pixels
        if not self.cap.isOpened():
            print("Unable to open camera")
            exit(1)

    def detect_person(self, frame):
        # Preprocess frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = torch.from_numpy(frame_rgb).float().permute(2, 0, 1).unsqueeze(0) / 255.0

        results = self.model(frame_rgb)
        # Find the maximum class score and its corresponding class for each anchor box
        class_scores, class_ids = torch.max(results[0, :, 5:], dim=1)
        print(f"Class IDs: {class_ids}")  # Debug line
        print(f"Class Scores: {class_scores}")  # Debug line
        # Check for persons; class ID for persons is 0
        persons = class_ids[(class_ids == 0) & (class_scores > 0.5)]  # Add score threshold
        return len(persons) > 0, results[0]

    def cleanup(self):
        # Clean up
        self.cap.release()
        cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    ai_vision = AIVisionIntegration()
