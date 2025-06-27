import torch
from transformers import YolosFeatureExtractor, YolosForObjectDetection
import cv2
from torchvision.ops import nms
from PIL import Image

feature_extractor = YolosFeatureExtractor.from_pretrained('hustvl/yolos-small')
model = YolosForObjectDetection.from_pretrained('hustvl/yolos-small').to('cuda')

def process_frame(frame, confidence_threshold=0.8, iou_threshold=0.5):

    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    inputs = feature_extractor(images=image, return_tensors="pt").to('cuda')
    outputs = model(**inputs)
    
    target_sizes = torch.tensor([image.size[::-1]])
    results = feature_extractor.post_process_object_detection(outputs, target_sizes=target_sizes)[0]
    
    scores = results["scores"]
    labels = results["labels"]
    boxes = results["boxes"]

    keep = scores > confidence_threshold
    scores = scores[keep]
    labels = labels[keep]
    boxes = boxes[keep]

    keep_indices = nms(boxes, scores, iou_threshold)
    boxes = boxes[keep_indices]
    scores = scores[keep_indices]
    labels = labels[keep_indices]

    for score, label, box in zip(scores, labels, boxes):
        box = [round(i, 2) for i in box.tolist()]
        xmin, ymin, xmax, ymax = box
        cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color=(0, 255, 0), thickness=2)
        label_text = f"{model.config.id2label[label.item()]}: {round(score.item(), 2)}"
        cv2.putText(frame, label_text, (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    
    frame = process_frame(frame)
    
    cv2.imshow('Real-time Object Detection', frame)
    
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()