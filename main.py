import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
from VisualNovelSubs.vns import subtitles
from VisualNovelSubs.vns import editor
from VisualNovelSubs.vns.ocr import load_ocr_data_from_json
from VisualNovelSubs.vns.ocr import crop_image

def validate_input(P):
    
    return P.isalnum()

class VNSEditorApp:

    def __init__(self, root):

        self.root = root

        self.root.title("VNS Editor")
        
        self.outputs_path = "outputs"
        self.projects_path = "projects"

        self.status_path = "status.json"

        self.editor_status = editor.EditorStatus("", False)

        self.editor_project = None

        self.show_hidden = tk.BooleanVar()
        self.show_hidden.set(self.editor_status.show_hidden)

        self.is_visible = tk.BooleanVar()
        self.is_visible.set(False)

        self.show_cropped_image  = tk.BooleanVar()
        self.show_cropped_image.set(True)

        self.last_frame_no = -1

        self.cropped_image = None

        self.languages = {}

        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="New project", command=self.new_project)
        file_menu.add_command(label="Load project", command=self.load_project)
        file_menu.add_command(label="Save project", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Export to SRT", command=self.export_to_srt)
        file_menu.add_command(label="Export to translated SRT", command=self.export_to_translated_srt)

        project_menu = tk.Menu(self.menubar, tearoff=0)
        project_menu.add_command(label="Change video path", command=self.change_video_path)
        project_menu.add_command(label="Change ocr data", command=self.change_ocr_data)
        project_menu.add_command(label="Reset sequences", command=self.reset_sequences)

        self.menubar.add_cascade(label="File", menu=file_menu)
        self.menubar.add_cascade(label="Project", menu=project_menu, state="disabled")

        self.root.rowconfigure(0, minsize=20)
        self.root.rowconfigure(8, minsize=20)
        self.root.columnconfigure(0, minsize=20)
        self.root.columnconfigure(5, minsize=20)
        self.root.columnconfigure(10, minsize=20)

        tk.Label(self.root, text="Sequences").grid(row=1, column=1, sticky=tk.W)

        self.show_hidden_checkbox = ttk.Checkbutton(self.root, text="Show hidden", variable=self.show_hidden, command=self.change_show_hidden)
        self.show_hidden_checkbox.grid(row=1, column=3, columnspan=2, sticky=tk.E)

        self.sequences_treeview = ttk.Treeview(self.root, columns=("sequence", "subs", "start_time", "end_time", "text"), height=24, selectmode="browse")
        self.sequences_treeview.column("#0", minwidth=0, width=0, stretch=False)
        self.sequences_treeview.column("sequence", width=50, anchor='center')
        self.sequences_treeview.column("subs", width=50, anchor='center')
        self.sequences_treeview.column("start_time", width=100, anchor='center')
        self.sequences_treeview.column("end_time", width=100, anchor='center')
        self.sequences_treeview.column("text", width=400)
        self.sequences_treeview.heading("#0", text="Index")
        self.sequences_treeview.heading("sequence", text="Sequence")
        self.sequences_treeview.heading("subs", text="Subs")
        self.sequences_treeview.heading("start_time", text="Start time")
        self.sequences_treeview.heading("end_time", text="End time")
        self.sequences_treeview.heading("text", text="Text")
        self.sequences_treeview.tag_configure('red', background='red')
        self.sequences_treeview.tag_configure('gray', background='lightgray')
        self.sequences_treeview.tag_configure('normal', background='white')
        self.sequences_treeview.grid(row=2, column=1, columnspan=3)
        self.sequences_treeview.bind("<<TreeviewSelect>>", self.select_sequences_treeview)
        self.sequences_treeview.bind("<Button-3>", self.right_click_sequences_treeview)

        self.sequences_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.sequences_treeview.yview)
        
        self.sequences_treeview.configure(yscrollcommand=self.sequences_scrollbar.set)

        self.sequences_scrollbar.grid(row=2, column=4, sticky='nse')

        tk.Button(self.root, text="Join sequences", command=self.join_sequences, width=25).grid(row=3, column=1, columnspan=4)

        tk.Label(self.root, text="Subs").grid(row=5, column=1, sticky=tk.W)

        self.is_visible_checkbox = ttk.Checkbutton(self.root, text="Visible", variable=self.is_visible, command=self.set_sequence_visibility)
        self.is_visible_checkbox.grid(row=5, column=3, columnspan=2, sticky=tk.E)

        self.subs_treeview = ttk.Treeview(self.root, columns=("start_time", "end_time", "text"), height=8, selectmode="browse")
        self.subs_treeview.column("#0", minwidth=0, width=0, stretch=False)
        self.subs_treeview.column("start_time", width=100, anchor='center')
        self.subs_treeview.column("end_time", width=100, anchor='center')
        self.subs_treeview.column("text", width=500)
        self.subs_treeview.heading("#0", text="Index")
        self.subs_treeview.heading("start_time", text="Start time")
        self.subs_treeview.heading("end_time", text="End time")
        self.subs_treeview.heading("text", text="Text")
        self.subs_treeview.tag_configure('gray', background='lightgray')
        self.subs_treeview.tag_configure('normal', background='white')
        self.subs_treeview.grid(row=6, column=1, columnspan=3)
        self.subs_treeview.bind("<<TreeviewSelect>>", self.select_subs_treeview)
        self.subs_treeview.bind("<Button-3>", self.right_click_subs_treeview)

        self.subs_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.subs_treeview.yview)
        
        self.subs_treeview.configure(yscrollcommand=self.subs_scrollbar.set)

        self.subs_scrollbar.grid(row=6, column=4, sticky='nse')
        
        tk.Button(self.root, text="Break sequence", command=self.break_sequence, width=25).grid(row=7, column=1, columnspan=4)

        self.image_label = tk.Label(self.root, text="Frame")
        self.image_label.grid(row=1, column=6, sticky=tk.W)

        self.canvas = tk.Canvas(self.root, width=854, height=480, bg='black')
        self.canvas.grid(row=2, column=6, columnspan=4)
        
        tk.Button(self.root, text="First frame", command=self.show_first_frame, width=15).grid(row=3, column=6, sticky=tk.E)
        tk.Button(self.root, text="Last frame", command=self.show_last_frame, width=15).grid(row=3, column=7, sticky=tk.W)

        self.show_cropped_image_checkbox = ttk.Checkbutton(self.root, text="Show cropped image", variable=self.show_cropped_image, command=self.change_state_cropped_image)
        self.show_cropped_image_checkbox.grid(row=3, column=9, sticky=tk.E)

        self.text_text = tk.Text(self.root, width=66, height = 4, padx=10, pady=10, font=('Arial', 16), wrap=tk.WORD)
        self.text_text.grid(row=5, column=6, rowspan=2, columnspan=4)

        tk.Button(self.root, text="Save text", command=self.set_sequence_text, width=15).grid(row=7, column=7, columnspan=2)
    
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.bind("<Control-s>", self.ctrl_s)

        self.root.bind("<Control-b>", self.ctrl_b)

        self.create_folders()
        
        self.load_editor_status()


    def create_folders(self):

        if not os.path.exists(self.outputs_path):
            os.mkdir(self.outputs_path)

        if not os.path.exists(self.projects_path):
            os.mkdir(self.projects_path)


    def save_editor_status(self):

        if self.editor_status:

            self.editor_status.show_hidden = self.show_hidden.get()

            editor.save_editor_status_to_json(self.status_path, self.editor_status)


    def load_editor_status(self):

        if os.path.exists(self.status_path):

            self.editor_status = editor.load_editor_status_from_json(self.status_path)

            if os.path.exists(self.editor_status.project_path):

                self.show_hidden.set(self.editor_status.show_hidden)

                self.editor_project = editor.load_editor_project_from_json(self.editor_status.project_path)

                self.show_project()

            else:

                self.editor_status.project_path = ""

    
    def change_show_hidden(self):

        if self.editor_project:

            self.load_sequences_treeview()


    def right_click_sequences_treeview(self, event):

        self.join_sequences()


    def right_click_subs_treeview(self, event):
        
        self.break_sequence()


    def ctrl_s(self, event):

        self.set_sequence_text()
        
        if self.editor_project:

            self.save_editor_status()

            editor.save_editor_project_to_json(self.editor_status.project_path, self.editor_project)


    def ctrl_b(self, event):

        self.is_visible.set(not self.is_visible.get())

        self.set_sequence_visibility()


    def on_closing(self):

        if self.editor_project:

            self.save_editor_status()

            editor.save_editor_project_to_json(self.editor_status.project_path, self.editor_project)
        
            self.root.destroy()
            
        else:

            self.root.destroy()


    def clear_sequences_treeview(self):

        for item in self.sequences_treeview.get_children():

            self.sequences_treeview.delete(item)


    def load_sequences_treeview(self, index= -1):

        self.last_frame_no = -1

        self.canvas.delete("all")

        self.text_text.delete('1.0', tk.END)

        self.clear_subs_treeview()
        
        self.clear_sequences_treeview()

        i = 0

        j = 1
        
        for sequence in self.editor_project.sequences:

            if not self.show_hidden.get() and not sequence.is_visible:

                j += 1

                continue

            sub = sequence.contracted_subtitles()

            start_time = subtitles.frame_to_time(sub.start_frame, self.editor_project.ocr_data.fps)

            end_time = subtitles.frame_to_time(sub.end_frame(), self.editor_project.ocr_data.fps)

            if i % 2 == 0:
            
                background_tag = "gray"

            else:

                background_tag = "normal"

            if not sequence.is_visible:
            
                background_tag = "red"

            self.sequences_treeview.insert(
                "",
                tk.END,
                text=f"{i}",
                values=(f"{j}", len(sequence.subtitles), start_time, end_time, sub.text),
                tag=(background_tag)
            )

            i += 1

            j += 1


        if index > -1:

            self.sequences_treeview.focus(self.sequences_treeview.get_children()[index])
            self.sequences_treeview.selection_set(self.sequences_treeview.get_children()[index])


    def select_sequences_treeview(self, event):

        if self.sequences_treeview.focus():

            sequence_index = self.get_sequence_index()

            len_sub = len(self.editor_project.sequences[sequence_index].subtitles)

            self.load_subs_treeview(len_sub - 1)


    def clear_subs_treeview(self):
        
        for item in self.subs_treeview.get_children():

            self.subs_treeview.delete(item)


    def load_subs_treeview(self, index= -1):

        self.clear_subs_treeview()
        
        sequence_index = self.get_sequence_index()
        
        if sequence_index > -1:

            sequence = self.editor_project.sequences[sequence_index]

            self.is_visible.set(sequence.is_visible)

            i = 0
            
            for sub in sequence.subtitles:

                start_time = subtitles.frame_to_time(sub.start_frame, self.editor_project.ocr_data.fps)

                end_time = subtitles.frame_to_time(sub.end_frame(), self.editor_project.ocr_data.fps)

                if i % 2 == 0:
                
                    background_tag = "gray"

                else:

                    background_tag = "normal"

                self.subs_treeview.insert(
                    "",
                    tk.END,
                    text=f"{i}",
                    values=(start_time, end_time, sub.text),
                    tag=(background_tag)
                )

                i += 1

            if index > -1:

                self.subs_treeview.focus(self.subs_treeview.get_children()[index])
                self.subs_treeview.selection_set(self.subs_treeview.get_children()[index])


    def select_subs_treeview(self, event):

        if self.subs_treeview.focus():

            sub = self.subs_treeview.item(self.subs_treeview.focus(), 'values')
            
            self.text_text.delete('1.0', tk.END)
            self.text_text.insert(tk.INSERT, sub[2])

            self.show_last_frame()

    
    def get_sequence_index(self):

        if self.sequences_treeview.focus():
        
            index = self.sequences_treeview.item(self.sequences_treeview.focus(), 'values')[0]

            return int(index) - 1

        else:

            return -1


    def get_sequences_treeview_index(self):

        if self.sequences_treeview.focus():
        
            index = self.sequences_treeview.item(self.sequences_treeview.focus(), 'text')

            return int(index)

        else:

            return -1


    def get_subs_treeview_index(self):

        if self.subs_treeview.focus():
        
            index = self.subs_treeview.item(self.subs_treeview.focus(), 'text')

            return int(index)

        else:

            return -1
        

    def change_state_cropped_image(self):

        if self.cropped_image:
                
            if self.show_cropped_image.get():

                self.canvas.itemconfig(self.cropped_image, state=tk.NORMAL)

            else:

                self.canvas.itemconfig(self.cropped_image, state=tk.HIDDEN)


    def resize_frame(self, frame, new_width, new_height):
            
            height, width = frame.shape[:2]

            aspect_ratio = width / height
            
            if new_width / aspect_ratio > new_height:
            
                new_width = int(new_height * aspect_ratio)
            
            else:
            
                new_height = int(new_width / aspect_ratio)

            frame = cv2.resize(frame, (new_width, new_height))

            return frame


    def load_image(self, frame_no, label_text, crop=True):

        if self.last_frame_no != frame_no and os.path.exists(self.editor_project.video_path):

            self.last_frame_no = frame_no

            self.image_label.config(text=label_text)

            video = cv2.VideoCapture(self.editor_project.video_path)

            if video.get(cv2.CAP_PROP_FRAME_COUNT) >= frame_no:

                video.set(cv2.CAP_PROP_POS_FRAMES, frame_no)

                ret, frame = video.read()

                if ret:

                    crop_frame = frame

                    canvas_width = self.canvas.winfo_width()
                    
                    canvas_height = self.canvas.winfo_height()

                    frame = self.resize_frame(frame, canvas_width, canvas_height)

                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                    image = Image.fromarray(frame)

                    self.tk_image = ImageTk.PhotoImage(image)
                
                    self.image = self.canvas.create_image(0, canvas_height, anchor=tk.SW, image=self.tk_image)

                    crop_frame = crop_image(crop_frame, self.editor_project.ocr_data.region)

                    crop_frame = self.resize_frame(crop_frame, canvas_width, canvas_height)

                    crop_frame = cv2.cvtColor(crop_frame, cv2.COLOR_BGR2RGB)
                
                    image = Image.fromarray(crop_frame)

                    self.tk_cropped_image = ImageTk.PhotoImage(image)

                    self.cropped_image = self.canvas.create_image(0, canvas_height, anchor=tk.SW, image=self.tk_cropped_image)

                    self.change_state_cropped_image()

                video.release()

            else:
        
                messagebox.showerror("Error", "The image cannot be loaded.")
    

    def show_first_frame(self):

        if self.subs_treeview.focus():

            sequence_index = self.get_sequence_index()

            sub_index = self.get_subs_treeview_index()

            frame_no = self.editor_project.sequences[sequence_index].subtitles[sub_index].start_frame
            
            self.load_image(frame_no, "First frame")

    
    def show_last_frame(self):

        if self.subs_treeview.focus():

            sequence_index = self.get_sequence_index()

            sub_index = self.get_subs_treeview_index()

            start_frame = self.editor_project.sequences[sequence_index].subtitles[sub_index].start_frame

            frame_no = self.editor_project.sequences[sequence_index].subtitles[sub_index].end_frame() - self.editor_project.ocr_data.frame_skip

            if frame_no < start_frame:

                frame_no = start_frame
            
            self.load_image(frame_no, "Last frame")


    def join_sequences(self):

        sequence_index = self.get_sequence_index()

        if sequence_index > 0:

            old_len_sequences = len(self.editor_project.sequences)

            self.editor_project.sequences = subtitles.join_sequences(self.editor_project.sequences, sequence_index - 1, sequence_index)

            if old_len_sequences != len(self.editor_project.sequences):

                sequences_treeview_index = self.get_sequences_treeview_index()

                self.load_sequences_treeview(index=(sequences_treeview_index - 1))


    def break_sequence(self):
        
        sequence_index = self.get_sequence_index()

        sub_index = self.get_subs_treeview_index()

        if sequence_index > -1 and sub_index > -1:

            old_len_sequences = len(self.editor_project.sequences)

            self.editor_project.sequences = subtitles.break_sequence(self.editor_project.sequences, sequence_index, sub_index)

            if old_len_sequences != len(self.editor_project.sequences):

                sequences_treeview_index = self.get_sequences_treeview_index()

                self.load_sequences_treeview(index=(sequences_treeview_index + 1))
    

    def set_sequence_visibility(self):
        
        sequence_index = self.get_sequence_index()

        sub_index = self.get_subs_treeview_index()

        if sequence_index > -1 and sub_index > -1:
        
            self.editor_project.sequences[sequence_index].is_visible = self.is_visible.get()

            if self.is_visible.get() or self.show_hidden.get():

                sequences_treeview_index = self.get_sequences_treeview_index()

                self.load_sequences_treeview(index=sequences_treeview_index)
            
            else:

                self.canvas.delete("all")

                self.text_text.delete('1.0', tk.END)

                self.load_sequences_treeview()
                

    def set_sequence_text(self):
        
        sequence_index = self.get_sequence_index()

        sub_index = self.get_subs_treeview_index()

        if sequence_index > -1 and sub_index > -1:

            self.editor_project.sequences[sequence_index].subtitles[sub_index].text = self.text_text.get("1.0", tk.END).strip()

            sequences_treeview_index = self.get_sequences_treeview_index()

            self.load_sequences_treeview(index=sequences_treeview_index)

            self.load_subs_treeview(index=sub_index)


    def show_project(self):

        self.menubar.entryconfig("Project", state="active")

        self.root.title("VNS Editor: " + os.path.splitext(os.path.basename(self.editor_status.project_path))[0])

        self.load_sequences_treeview()


    def browse_ocr_data_files(self):

        ocr_data_path = filedialog.askopenfilename(filetypes=[("ocr data files", "*.ocrdata")])

        if ocr_data_path:

            self.ocr_data_path.config(state='normal')

            self.ocr_data_path.delete(0, tk.END)

            self.ocr_data_path.insert(0, ocr_data_path)

            self.ocr_data_path.config(state='disable')


    def browse_mp4_files(self):

        mp4_path = filedialog.askopenfilename(filetypes=[("mp4 files", "*.mp4")])

        if mp4_path:

            self.mp4_path.config(state='normal')

            self.mp4_path.delete(0, tk.END)

            self.mp4_path.insert(0, mp4_path)

            self.mp4_path.config(state='disable')
    

    def create_project(self):

        if self.project_name.get() and self.ocr_data_path.get() and self.mp4_path.get():

            project_path = os.path.join(self.projects_path, self.project_name.get()) + ".project"

            if os.path.exists(project_path):

                messagebox.showwarning("Warning", "A project with this name already exists.")

                return

            self.editor_status.project_path = project_path

            self.save_editor_status()

            video_path = self.mp4_path.get()
            ocr_data = load_ocr_data_from_json(self.ocr_data_path.get())
            sequences = subtitles.subtitles_to_sequences(ocr_data.subtitles)

            self.editor_project = editor.EditorProject(video_path, ocr_data, sequences)
            
            editor.save_editor_project_to_json(self.editor_status.project_path, self.editor_project)

            self.show_project()

            self.create_project_window.destroy()

            messagebox.showinfo("Info", "Project created.")
        
        else:

            messagebox.showerror("Error", "Required fields are missing.")
    

    def new_project(self):

        self.create_project_window = tk.Toplevel(self.root)

        self.create_project_window.title("Create project")
        
        validation = self.create_project_window.register(validate_input)

        self.create_project_window.rowconfigure(0, minsize=20)
        self.create_project_window.rowconfigure(5, minsize=20)
        self.create_project_window.columnconfigure(0, minsize=20)
        self.create_project_window.columnconfigure(5, minsize=20)

        tk.Label(self.create_project_window, text="Project name: ").grid(row=1, column=1, padx=10, pady=10, sticky=tk.E)
        self.project_name = tk.Entry(self.create_project_window, width=30, validate="key", validatecommand=(validation, "%P"))
        self.project_name.grid(row=1, column=2, columnspan=2, padx=10, pady=10)

        tk.Label(self.create_project_window, text="OCR data: ").grid(row=2, column=1, padx=10, pady=10, sticky=tk.E)
        self.ocr_data_path = tk.Entry(self.create_project_window, width=30, state="disabled")
        self.ocr_data_path.grid(row=2, column=2, columnspan=2, padx=10, pady=10)
        tk.Button(self.create_project_window, text="Browse", command=self.browse_ocr_data_files).grid(row=2, column=4, padx=10, pady=10)

        tk.Label(self.create_project_window, text="MP4 file: ").grid(row=3, column=1, padx=10, pady=10, sticky=tk.E)
        self.mp4_path = tk.Entry(self.create_project_window, width=30, state="disabled")
        self.mp4_path.grid(row=3, column=2, columnspan=2, padx=10, pady=10)
        tk.Button(self.create_project_window, text="Browse", command=self.browse_mp4_files).grid(row=3, column=4, padx=10, pady=10)
        
        tk.Button(self.create_project_window, text="Accept", width=10, command=self.create_project).grid(row=4, column=2, padx=10, pady=10)
        tk.Button(self.create_project_window, text="Cancel", width=10, command=self.create_project_window.destroy).grid(row=4, column=3, padx=10, pady=10)
        
        self.create_project_window.resizable(False, False)
    
        self.create_project_window.grab_set()

        self.root.wait_window(self.create_project_window)


    def save_project(self):

        if self.editor_project:

            self.save_editor_status()

            editor.save_editor_project_to_json(self.editor_status.project_path, self.editor_project)
        
            messagebox.showinfo("Info", "Project Saved.")

        else:
        
            messagebox.showerror("Error", "No project has been selected.")


    def load_project(self):

        project_path = filedialog.askopenfilename(filetypes=[("project files", "*.project")])

        if project_path:

            self.editor_status.project_path = project_path

            self.save_editor_status()

            self.editor_project = editor.load_editor_project_from_json(self.editor_status.project_path)

            self.show_project()

            messagebox.showinfo("Info", "Project loaded.")

    
    def export_to_srt(self):

        if self.editor_project:

            srt_path = os.path.join(self.outputs_path, os.path.splitext(os.path.basename(self.editor_status.project_path))[0]) + ".srt"

            subs = subtitles.sequences_to_subtitles(self.editor_project.sequences)

            fps = self.editor_project.ocr_data.fps

            subtitles.save_subtitles_to_srt(srt_path, subs, fps)

            messagebox.showinfo("Info", "SRT exported.")

        else:
        
            messagebox.showerror("Error", "No project has been selected.")


    def choose_language(self):

        src = [key for key, value in self.languages.items() if value == self.source_language_combobox.get()][0]

        dest = [key for key, value in self.languages.items() if value == self.destination_language_combobox.get()][0]

        srt_path = os.path.join(self.outputs_path, os.path.splitext(os.path.basename(self.editor_status.project_path))[0]) + "." + dest + ".srt"

        subs = subtitles.sequences_to_subtitles(self.editor_project.sequences)

        subs = editor.translate_subs(subs, src=src, dest=dest)

        fps = self.editor_project.ocr_data.fps

        subtitles.save_subtitles_to_srt(srt_path, subs, fps)

        self.choose_language_window.destroy()

        messagebox.showinfo("Info", "Translated SRT exported.")


    def export_to_translated_srt(self):

        if self.editor_project:

            if not self.languages:

                self.languages = editor.get_languages()

            self.choose_language_window = tk.Toplevel(self.root)

            self.choose_language_window.title("Choose language")

            self.choose_language_window.rowconfigure(0, minsize=20)
            self.choose_language_window.rowconfigure(4, minsize=20)
            self.choose_language_window.columnconfigure(0, minsize=20)
            self.choose_language_window.columnconfigure(3, minsize=20)

            tk.Label(self.choose_language_window, text="Source language:").grid(row=1, column=1, padx=10, pady=10, sticky=tk.E)
            self.source_language_combobox = ttk.Combobox(self.choose_language_window, state="readonly", values=list(self.languages.values()))
            self.source_language_combobox.set('english')
            self.source_language_combobox.grid(row=1, column=2, padx=10, pady=10, sticky=tk.W)
            
            tk.Label(self.choose_language_window, text="Destination language:").grid(row=2, column=1, padx=10, pady=10, sticky=tk.E)
            self.destination_language_combobox = ttk.Combobox(self.choose_language_window, state="readonly", values=list(self.languages.values()))
            self.destination_language_combobox.set('spanish')
            self.destination_language_combobox.grid(row=2, column=2, padx=10, pady=10, sticky=tk.W)
            
            tk.Button(self.choose_language_window, text="Accept", width=10, command=self.choose_language).grid(row=3, column=1, padx=10, pady=10, sticky=tk.E)
            tk.Button(self.choose_language_window, text="Cancel", width=10, command=self.choose_language_window.destroy).grid(row=3, column=2, padx=10, pady=10, sticky=tk.W)
            
            self.choose_language_window.resizable(False, False)
        
            self.choose_language_window.grab_set()

            self.root.wait_window(self.choose_language_window)

        else:
        
            messagebox.showerror("Error", "No project has been selected.")


    def change_video_path(self):

        video_path = filedialog.askopenfilename(filetypes=[("mp4 files", "*.mp4")])

        if video_path:

            self.editor_project.video_path = video_path


    def change_ocr_data(self):

        ocr_data_path = filedialog.askopenfilename(filetypes=[("ocr data files", "*.ocrdata")])

        if ocr_data_path:

            self.editor_project.ocr_data = load_ocr_data_from_json(ocr_data_path)

            self.editor_project.sequences = subtitles.subtitles_to_sequences(self.editor_project.ocr_data.subtitles)

            self.show_project()
    

    def reset_sequences(self):

        if messagebox.askokcancel("Reset Sequences", "Are you sure you want to reset the sequences? This process will delete all the work done so far."):

            self.editor_project.sequences = subtitles.subtitles_to_sequences(self.editor_project.ocr_data.subtitles)

            self.load_sequences_treeview()


if __name__ == "__main__":
    
    root = tk.Tk()
    
    app = VNSEditorApp(root)

    root.resizable(False,False)

    root.mainloop()