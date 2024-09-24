import cv2
import numpy as np
from ultralytics import YOLO

class AIVisionIntegration:
    def __init__(self, model_type='pose'):
        # Initialize YOLO model based on the type
        if model_type == 'pose':
            self.model = YOLO('yolov8s-pose.pt')
        elif model_type == 'segmentation':
            self.model = YOLO('yolov8s-seg.pt')
        else:
            self.model = YOLO('yolov8s.pt')

        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)  # Adjust '0' to your camera ID
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set the width 
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set the height 
        if not self.cap.isOpened():
            print("Unable to open camera")
            exit(1)
    # TODO: implement track

    def detect_person(self, frame):
        # Preprocess frame
        results = self.model(frame)
        
        # output format
        persons = []
        for result in results:
            for box in result.boxes:
                if box.cls == 0 and box.conf > 0.5:  # Assuming '0' is the class ID for person
                    persons.append(box)
        self.display_detection(frame, results)
        return len(persons) > 0, results

    def get_person_pose(self, frame):
        # Perform pose estimation using YOLOv8-pose
        results = self.model(frame)
        poses = []
        for result in results:
            for keypoint in result.keypoints:
                poses.append(keypoint.xy)
        self.display_pose(frame, poses)
        return poses

    def instance_segmentation(self, frame):
        # Perform instance segmentation
        results = self.model(frame)
        masks = []
        for result in results:
            if hasattr(result, 'masks'):
                masks.extend(result.masks.data.cpu().numpy())
        self.display_segmentation(frame, results)
        return masks

    def classification(self, frame):
        # Perform classification
        results = self.model(frame)
        classifications = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls)
                confidence = box.conf.item()  # Convert tensor to float
                classifications.append((class_id, confidence))
        self.display_classification(frame, classifications)
        return classifications

    def display_detection(self, frame, results):
        # Display the frame with bounding boxes around detected objects
        for result in results:
            for box in result.boxes:
                if box.conf > 0.4:  # Display all classes with confidence > 0.4
                    x1, y1, x2, y2 = box.xyxy[0]
                    class_id = int(box.cls)
                    confidence = box.conf.item()  # Convert tensor to float

                    #  the model provides class names
                    class_name = self.model.names[class_id] if hasattr(self.model, 'names') else str(class_id)

                    # Draw bounding box
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                    # Display class name and confidence score
                    label = f"{class_id}: {class_name} ({confidence:.2f})"
                    cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cleanup()
            exit(0)

    def display_pose(self, frame, poses):
        # Draw keypoints and lines on the frame
        for pose in poses:
            keypoints = pose[0]
            # Draw keypoints
            for x, y in keypoints:
                if x > 0 and y > 0:  # Only draw valid keypoints
                    cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)
            # Draw lines between keypoints
            skeleton = [
                (0, 1), (0, 2), (1, 3), (2, 4),  # Head
                (0, 5), (0, 6),  # Shoulders
                (5, 7), (7, 9),  # Left arm
                (6, 8), (8, 10),  # Right arm
                (5, 11), (6, 12),  # Torso
                (11, 13), (13, 15),  # Left leg
                (12, 14), (14, 16)  # Right leg
            ]
            for start, end in skeleton:
                if keypoints[start][0] > 0 and keypoints[start][1] > 0 and keypoints[end][0] > 0 and keypoints[end][1] > 0:
                    cv2.line(frame, (int(keypoints[start][0]), int(keypoints[start][1])), 
                             (int(keypoints[end][0]), int(keypoints[end][1])), (0, 255, 0), 2)
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cleanup()
            exit(0)

    def display_segmentation(self, frame, results):
        # Check if the color map is already initialized
        if not hasattr(self, 'color_map'):
            # Generate a fixed color map for the classes
            self.color_map = np.random.randint(0, 255, size=(len(self.model.names), 3), dtype=np.uint8)

        # Display the frame with segmentation masks
        for result in results:
            if hasattr(result, 'masks'):
                for mask, box in zip(result.masks.data.cpu().numpy(), result.boxes):
                    class_id = int(box.cls)
                    color = self.color_map[class_id]
                    mask = mask > 0.5  # Threshold the mask
                    frame[mask] = frame[mask] * 0.5 + color * 0.5  # Blend the color with the frame

        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cleanup()
            exit(0)

    def display_classification(self, frame, classifications):
        # Generate a fixed color map for the classes if not already created
        if not hasattr(self, 'color_map'):
            self.color_map = np.random.randint(0, 255, size=(len(self.model.names), 3), dtype=np.uint8)

        # Display the frame with classification results
        height, width, _ = frame.shape
        y_offset = height - 20  # Start displaying labels from the bottom

        for class_id, confidence in classifications:
            # Assuming the model provides class names
            class_name = self.model.names[class_id] if hasattr(self.model, 'names') else str(class_id)

            # Get the color for the class
            color = self.color_map[class_id].tolist()

            # Display class name and confidence score
            label = f"{class_name} ({confidence:.2f})"
            (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, (10, y_offset - text_height - baseline), (10 + text_width, y_offset + baseline), color, cv2.FILLED)
            cv2.putText(frame, label, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            y_offset -= (text_height + baseline + 10)  # Move up for the next label

        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cleanup()
            exit(0)

    def cleanup(self):
        # Clean up
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Initialize 'pose', 'segmentation','classification' or 'detect_person' model
    ai_vision = AIVisionIntegration(model_type='pose')

    while True:
        ret, frame = ai_vision.cap.read()
        if not ret:
            break

        #-----------------------------------------------------------------------------
        # Test object detection(detect_person)
        #person_detected, results = ai_vision.detect_person(frame)
        #print(f"Person detected: {person_detected}")

        # Test get_person_pose
        poses = ai_vision.get_person_pose(frame)
        print(f"Poses: {poses}")

        # Test instance_segmentation
        #masks = ai_vision.instance_segmentation(frame)
        #print(f"Masks: {masks}")

        # Test classification
        #classifications = ai_vision.classification(frame)
        #print(f"Classifications: {classifications}")

    # Cleanup 
    ai_vision.cleanup()