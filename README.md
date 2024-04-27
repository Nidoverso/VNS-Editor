# VNS Editor

VNS Editor is a Tkinter-based application designed to simplify and enhance the results of OCR performed with [VNS OCR](https://github.com/nidoverso/vns-ocr).

## Objective

Process the result obtained from [VNS OCR](https://github.com/nidoverso/vns-ocr) to obtain usable subtitles and export them to ".srt" files.

## Usage

### New/Load Project

- A project is created by specifying the path to a video and loading a `.ocrdata` file, which is the output of [VNS OCR](https://github.com/nidoverso/vns-ocr).
- Once created, the project can be saved to a file for resuming work from where you left off.

### Sequences

- When loading a project, a list of the current sequences will be displayed. Initially, each sequence will contain a single subtitle. You can select to simplify the subtitles before starting the project, it is recommended to leave it checked.
- By clicking on a sequence, you can see the subtitles it contains and their visibility. Invisible subtitles will not be included in the final SRT file.

### Subtitles

- Clicking on a subtitle will display its text and allow you to make edits.
- The application will automatically show the last frame where this text appeared and the first frame where it appeared.

### Show Cropped Image

- If the "Show Cropped Image" option is enabled, you can view the region of the image that the program read during OCR.

### Save Changes

- The "Save Text" option allows you to save the changes made to the text.

### Merge and Split Sequences

- "Join Sequences": With a selected sequence, you can merge it with the preceding sequence. The subtitles from this sequence will be added to the previous one, including the timestamp.
- "Break Sequence": By selecting a subtitle, you can split the sequence starting from that subtitle.

## Shortcuts

- Right-click (in the Sequences list): Performs the "Join Sequences" action.
- Right-click (in the Subtitles list): Performs the "Break Sequence" action.
- Ctrl + S: Saves the current text.
- Ctrl + B: Toggles the visibility of the selected sequence.

## SRT Menu

### Export SRT

- Export the current project to SRT.

### Translate SRT

- Translates an SRT file from the specified language to the desired language. You can translate any SRT file regardless of whether it was created using [VNS Editor](https://github.com/nidoverso/vns-editor) or not.

### Merge SRTs

- Merge two SRT files into one. This function has been created thinking in visual novels that change the place where the text is shown during the game. With this idea in mind the process would be to make two or more OCRs, each one with a part of the screen, then create a project in the editor for each of them, export the result to SRT and finally merge them into one. You can merge any SRT file regardless of whether it was created using [VNS Editor](https://github.com/nidoverso/vns-editor) or not.

## License

VNS Editor is distributed under the [GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.en.html), just like VisualNovelSubs and VNS-OCR. This ensures that the source code is available, and you can modify it to suit your needs, while respecting the terms of the license.