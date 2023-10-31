# VNS Editor

VNS Editor is a Tkinter-based application designed to simplify and enhance the results of OCR performed with [VNS OCR](https://github.com/nidoverso/vns-ocr).

## Objective

The results obtained from [VNS OCR](https://github.com/nidoverso/vns-ocr) may not always be accurate and can include repeated subtitles. To address this issue, VNS Editor enables the easy merging and splitting of subtitle sequences. For example, it allows you to combine the following sequences: "Hello", "Hello, how are", "Hello, How are you?", into a single sequence "Hello, How are you?".

## Usage

### Create/Load Project

- A project is created by specifying the path to a video and loading a `.ocrdata` file, which is the output of [VNS OCR](https://github.com/nidoverso/vns-ocr).
- Once created, the project can be saved to a file for resuming work from where you left off.

### Sequences

- When loading a project, a list of the current sequences will be displayed. Initially, each sequence will contain a single subtitle.
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
- Ctrl + S: Saves the current text and the current project state.
- Ctrl + B: Toggles the visibility of the selected sequence.

## License

VNS Editor is distributed under the [GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.en.html), just like VisualNovelSubs and VNS-OCR. This ensures that the source code is available, and you can modify it to suit your needs, while respecting the terms of the license.