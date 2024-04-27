import json
from .subtitles import Sequence
from .ocr import OCRData

class EditorStatus:
    
    def __init__(self, project_path, show_hidden):

        self.project_path = project_path

        self.show_hidden = show_hidden

    def to_json(self):
        
        data = {
            "project_path": self.project_path,
            "show_hidden": self.show_hidden
        }
        
        return json.dumps(data, indent=4)

    @classmethod
    def from_json(cls, json_str):
        
        data = json.loads(json_str)

        return cls(**data)


class EditorProject:
    
    def __init__(self, video_path, ocr_data, sequences):

        self.video_path = video_path

        self.ocr_data = ocr_data

        self.sequences = sequences

    def to_json(self):
        
        data = {
            "video_path": self.video_path,
            "ocr_data": self.ocr_data.to_json(),
            "sequences": [sequence.to_json() for sequence in self.sequences]
        }

        return json.dumps(data, indent=4)

    @classmethod
    def from_json(cls, json_str):
    
        data = json.loads(json_str)
        
        ocr_data = OCRData.from_json(data["ocr_data"])
        
        sequences = [Sequence.from_json(sequence) for sequence in data["sequences"]]
        
        return cls(data["video_path"], ocr_data, sequences)


def save_editor_status_to_json(json_path, editor_status):

    editor_status_json = editor_status.to_json()

    with open(json_path, "w") as json_file:
        
        json_file.write(editor_status_json)


def load_editor_status_from_json(json_path):

    with open(json_path, "r") as json_file:

        editor_status_json = json_file.read()

    return EditorStatus.from_json(editor_status_json)


def save_editor_project_to_json(json_path, editor_project):

    editor_project_json = editor_project.to_json()

    with open(json_path, "w") as json_file:
        
        json_file.write(editor_project_json)


def load_editor_project_from_json(json_path):

    with open(json_path, "r") as json_file:

        editor_project_json = json_file.read()

    return EditorProject.from_json(editor_project_json)