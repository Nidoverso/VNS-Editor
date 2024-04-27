import json

class Subtitle:
    
    def __init__(self, start_frame, duration, text):
    
        self.start_frame = start_frame
    
        self.duration = duration
    
        self.text = text
    
    def __str__(self):
    
        return f"Start Frame: {self.start_frame}, Duration: {self.duration}, Text: {self.text}"

    def end_frame(self):
        
        return self.start_frame + self.duration
    
    def clean_text(self):

        if self.text:

            # Replace line breaks and large blanks

            self.text = self.text.replace("\n", " ")
            self.text = self.text.replace("   ", " ")
            self.text = self.text.replace("  ", " ")

            # Replace strange symbols

            self.text = self.text.replace("|", "I")
            self.text = self.text.replace("[", "I")
            self.text = self.text.replace("]", "I")
            self.text = self.text.replace("{", "I")
            self.text = self.text.replace("}", "I")
            self.text = self.text.replace("‘", "'")
            self.text = self.text.replace("’", "'")
            self.text = self.text.replace('“', '"')
            self.text = self.text.replace('”', '"')
            self.text = self.text.replace("''", "'")
            self.text = self.text.replace('""', '"')
            self.text = self.text.replace('«', '')
            self.text = self.text.replace('»', '')
            self.text = self.text.replace('*', '')
            self.text = self.text.replace('~', '')
            self.text = self.text.replace('-', '')

            # Replace ellipses

            self.text = self.text.replace(", ,", ",,")
            self.text = self.text.replace(", .", ",.")
            self.text = self.text.replace(". ,", ".,")
            self.text = self.text.replace(". .", "..")

            self.text = self.text.replace(",,,", "...")
            self.text = self.text.replace(",,.", "...")
            self.text = self.text.replace(",.,", "...")
            self.text = self.text.replace(",..", "...")
            self.text = self.text.replace(".,,", "...")
            self.text = self.text.replace(".,.", "...")
            self.text = self.text.replace("..,", "...")

            # Eliminate empty spaces at the beginning and at the end
            
            self.text = self.text.strip()

            # If the last character is a quotation mark and the first character is not a quotation mark, quotation marks are added at the beginning.

            if len(self.text) > 1 and self.text[0] != '"' and self.text[-1] == '"':
                self.text = '"' + self.text

            # If the last character is a comma, the comma becomes a period.

            if len(self.text) > 0 and self.text[-1] == ",":

                self.text = self.text[:-1] + "."

            # If the penultimate character is a comma and the last character is a quotation mark, the comma becomes a period.

            if len(self.text) > 1 and self.text[-2] == "," and self.text[-1] == '"':
                
                self.text = self.text[:-2] + "." + self.text[-1:]

            # The text is scrolled through looking for the pattern (comma, space, capital letter) if found, it is replaced by (period, space, capital letter).

            new_text = ""

            i = 0

            while i < len(self.text):

                new_text += self.text[i]

                if i < len(self.text) - 2 and self.text[i] == ',' and self.text[i + 1] == ' ' and self.text[i + 2].isupper():

                    new_text = new_text[:-1] + '. '
                    
                    i += 2 
                
                else:
                    
                    i += 1

            self.text = new_text


    def to_json(self):
        
        data = {
            "start_frame": self.start_frame,
            "duration": self.duration,
            "text": self.text
        }
        
        return json.dumps(data, indent=4)
    
    @classmethod
    def from_json(cls, json_str):

        data = json.loads(json_str)

        return cls(data["start_frame"], data["duration"], data["text"])


class Sequence:
    
    def __init__(self, is_visible, subtitles):
        
        self.is_visible = is_visible
        
        self.subtitles = subtitles
    
    def __str__(self):
    
        return f"Is Visible: {self.is_visible}, Contracted Subtitles: {self.contracted_subtitles()}"

    def contracted_subtitles(self):

        start_frame = self.subtitles[0].start_frame

        duration = self.subtitles[len(self.subtitles) - 1].end_frame() - start_frame

        text = self.subtitles[len(self.subtitles) - 1].text

        return Subtitle(start_frame, duration, text)
    
    def print_subtitles(self):

        for s in self.subtitles:

            print(str(s))

    def to_json(self):
        
        data = {
            "is_visible": self.is_visible,
            "subtitles": [subtitle.to_json() for subtitle in self.subtitles]
        }

        return json.dumps(data, indent=4)
    
    @classmethod
    def from_json(cls, json_str):

        data = json.loads(json_str)
        
        subtitles = [Subtitle.from_json(subtitle) for subtitle in data["subtitles"]]
        
        return cls(data["is_visible"], subtitles)


def clean_subtitles(subtitles):

    cleaned_subtitles = subtitles

    for sub in subtitles:

        sub.clean_text()

    return cleaned_subtitles


def same_text(text1, text2, error):

    if text1 == text2:

        return True
    
    if text2.startswith(text1):

        return True
    
    if len(text2) >= len(text1) > (error + 2):
    
        i = 1

        while i < error + 1:

            if text2[:-i].startswith(text1[:-i]):
                
                return True

            i += 1
    
    if len(text2) >= len(text1)  > (error + 2):
        
        i = 1

        while i < error + 1:
          
            j = 1
            
            while j < error + 1:

                if text2[j:].startswith(text1[i:]):

                    return True
                
                j += 1

            i += 1

    return False


def simplify_subtitles(subtitles, error=3):

    simplified_subtitles = []
    
    i = 0

    while i < len(subtitles):
        
        subtitle = subtitles[i]

        if not subtitle.text:

            i += 1
            
            continue

        while (i + 1) < len(subtitles) and subtitles[(i + 1)].start_frame == subtitle.end_frame() and same_text(subtitle.text, subtitles[(i + 1)].text, error=error):

            subtitle.duration += subtitles[(i + 1)].duration
            
            subtitle.text = subtitles[(i + 1)].text

            i += 1

        simplified_subtitles.append(subtitle)

        i += 1

    return simplified_subtitles


def subtitles_to_sequences(subtitles):

    sequences = []

    for subtitle in subtitles:

        sequences.append(Sequence(True, [subtitle]))

    return sequences


def sequences_to_subtitles(sequences):

    subtitles = []

    for sequence in sequences:

        if sequence.is_visible:

            subtitles.append(sequence.contracted_subtitles())

    return subtitles


def join_sequences(sequences, index, target_index):

    if len(sequences) > index > -1 and len(sequences) > target_index > -1 and target_index > index:
        
        joined_sequences = sequences[:index + 1] + sequences[target_index + 1:]

        for i in range(index + 1, target_index + 1):
            
            joined_sequences[index].subtitles += sequences[i].subtitles

        return joined_sequences
    
    else:

        print("Indexes out of range.")

        return sequences


def break_sequence(sequences, sequence_index, subtitle_index):

    if len(sequences) > sequence_index > -1 and len(sequences[sequence_index].subtitles) > subtitle_index > 0:

        old_sequence = Sequence(sequences[sequence_index].is_visible, sequences[sequence_index].subtitles[:subtitle_index])

        new_sequence = Sequence(True, sequences[sequence_index].subtitles[subtitle_index:])
    
        breaked_sequences = sequences[:sequence_index] + [old_sequence, new_sequence] + sequences[sequence_index + 1:]

        return breaked_sequences
    
    else:

        print("Indexes out of range.")

        return sequences


def frame_to_time(frame_no, fps):

    time_in_seconds = frame_no / fps

    hours = time_in_seconds / 3600
    
    minutes = (time_in_seconds % 3600) / 60
    
    seconds = time_in_seconds % 60

    milliseconds = int((time_in_seconds % 1) * 1000)
    
    time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}.{int(milliseconds):03d}"

    return time


def subtitles_to_srt_subtitles(subtitles, fps):

    srt_subtitles = []

    for subtitle in subtitles:

        start_time = frame_to_time(subtitle.start_frame, fps)

        end_time = frame_to_time(subtitle.end_frame(), fps)

        text = subtitle.text
        
        srt_subtitles.append([start_time, end_time, text])

    return srt_subtitles