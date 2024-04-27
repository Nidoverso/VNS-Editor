import platform
import json
import cv2
import pytesseract
from .subtitles import Subtitle

if platform.system() == 'Windows':

    pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

class OCRStatus:
    
    def __init__(self, video_path, number_of_sample_frames, sample_frames, region, default_start_end, start_frame, end_frame, frame_skip, queue):

        self.video_path = video_path

        self.number_of_sample_frames = number_of_sample_frames

        self.sample_frames = sample_frames

        self.region = region

        self.default_start_end = default_start_end

        self.start_frame = start_frame

        self.end_frame = end_frame

        self.frame_skip = frame_skip

        self.queue = queue

    def to_json(self):
        
        data = {
            "video_path": self.video_path,
            "number_of_sample_frames": self.number_of_sample_frames,
            "sample_frames": self.sample_frames,
            "region": self.region,
            "default_start_end": self.default_start_end,
            "start_frame": self.start_frame,
            "end_frame": self.end_frame,
            "frame_skip": self.frame_skip,
            "queue": self.queue
        }
        
        return json.dumps(data, indent=4)

    @classmethod
    def from_json(cls, json_str):
        
        data = json.loads(json_str)

        return cls(**data)


def save_ocr_status_to_json(json_path, ocr_status):

    ocr_status_json = ocr_status.to_json()

    with open(json_path, "w") as json_file:
        
        json_file.write(ocr_status_json)


def load_ocr_status_from_json(json_path):

    with open(json_path, "r") as json_file:

        ocr_status_json = json_file.read()

    return OCRStatus.from_json(ocr_status_json)


class OCRData:
    
    def __init__(self, fps, frame_count, region, frame_skip, subtitles):

        self.fps = fps

        self.frame_count = frame_count

        self.region = region

        self.frame_skip = frame_skip

        self.subtitles = subtitles

    def to_json(self):
        
        data = {
            "fps": self.fps,
            "frame_count": self.frame_count,
            "region": self.region,
            "frame_skip": self.frame_skip,
            "subtitles": [subtitle.to_json() for subtitle in self.subtitles]
        }
        
        return json.dumps(data, indent=4)
    
    @classmethod
    def from_json(cls, json_str):

        data = json.loads(json_str)
        
        subtitles = [Subtitle.from_json(subtitle) for subtitle in data["subtitles"]]
        
        return cls(data["fps"], data["frame_count"], data["region"], data["frame_skip"], subtitles)
    

def save_ocr_data_to_json(json_path, ocr_data):

    ocr_data_json = ocr_data.to_json()

    with open(json_path, "w") as json_file:
        
        json_file.write(ocr_data_json)


def load_ocr_data_from_json(json_path):

    with open(json_path, "r") as json_file:

        ocr_data_json = json_file.read()

    return OCRData.from_json(ocr_data_json)


def read_image(image):

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    text = pytesseract.image_to_string(image)

    return text


def crop_image(image, region):

    cropped_image = image

    x, y, width, height = region

    img_height, img_width = image.shape[:2]

    if img_height >= (y + height) and img_width >= (x + width):

        cropped_image = image[y : y + height, x : x + width]

    else:

        print("Region out of image.")

    return cropped_image


# Start Frame inclusive, End Frame exclusive

def read_video(video_path, region, start_frame=0, end_frame=1000000000, frame_skip=10):
    
    subtitles = []

    video = cv2.VideoCapture(video_path)

    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    fps = video.get(cv2.CAP_PROP_FPS)

    if start_frame < 0:

        start_frame = 0

    if end_frame > frame_count:

        end_frame = frame_count

    frame_numbers = [i for i in range(start_frame, end_frame, frame_skip)]

    i = 1

    for frame_number in frame_numbers:
        
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        ret, frame = video.read()

        image = crop_image(frame, region)

        duration = frame_skip

        if (frame_number + duration) > end_frame:

            duration = end_frame - frame_number

        text = read_image(image)

        subtitles.append(Subtitle(int(frame_number), int(duration), text))

        print(f"Reading frame... {i}/{len(frame_numbers)}", end="\r")

        i += 1

    video.release()

    return fps, frame_count, subtitles


def get_sample_frames(video_path, number_of_sample_frames):

    video = cv2.VideoCapture(video_path)

    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)

    video.release()

    if number_of_sample_frames > frame_count:

        number_of_sample_frames = frame_count

    sample_frames = [int(i * (frame_count/(number_of_sample_frames + 1))) for i in range(1, number_of_sample_frames + 1)]

    return sample_frames