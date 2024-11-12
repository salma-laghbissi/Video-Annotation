
import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import json
import os

class VideoAnnotatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Annotator")

        # Set the window to maximized mode (not fullscreen)
        self.root.state("zoomed")

        # Get the screen width and height, then set the target width and height to be 75% of these values
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.target_width = int(screen_width * 0.75)
        self.target_height = int(screen_height * 0.75)

        # Video panel
        self.video_panel = tk.Label(self.root)
        self.video_panel.pack(expand=True, fill=tk.BOTH)

        # Controls and input fields for play/pause, forward, backward, annotate, and save
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.backward_button = tk.Button(control_frame, text="<<", command=self.backward_10)
        self.backward_button.grid(row=0, column=0, padx=5)

        self.backward_1_button = tk.Button(control_frame, text="<", command=self.backward_1)
        self.backward_1_button.grid(row=0, column=1, padx=5)

        self.play_button = tk.Button(control_frame, text="Play/Pause", command=self.play_pause)
        self.play_button.grid(row=0, column=2, padx=5)

        self.forward_1_button = tk.Button(control_frame, text=">", command=self.forward_1)
        self.forward_1_button.grid(row=0, column=3, padx=5)

        self.forward_button = tk.Button(control_frame, text=">>", command=self.forward_10)
        self.forward_button.grid(row=0, column=4, padx=5)

        tk.Label(control_frame, text="Label:").grid(row=0, column=5, padx=5)
        self.label_input = tk.Entry(control_frame, width=15)
        self.label_input.grid(row=0, column=6, padx=5)

        tk.Label(control_frame, text="Team:").grid(row=0, column=7, padx=5)
        self.team_input = tk.Entry(control_frame, width=15)
        self.team_input.grid(row=0, column=8, padx=5)

        self.annotate_button = tk.Button(control_frame, text="Annotate Frame", command=self.annotate_frame)
        self.annotate_button.grid(row=0, column=9, padx=5)

        # Open video file dialog
        self.video_path = filedialog.askopenfilename(title="Select Video", filetypes=[("Video files", "*.mp4 *.mkv *.mov")])
        self.cap = cv2.VideoCapture(self.video_path)

        # Video information
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.is_playing = False
        self.current_frame = 0
        self.annotations = []  # List to store annotations
        self.video_dir = os.path.dirname(self.video_path)  # Directory of the video
        self.url_local = os.path.splitext(os.path.basename(self.video_path))[0]  # Extracting filename as URL local

        # Path to JSON file
        self.annotation_file_path = os.path.join(self.video_dir, f"{self.url_local}_annotations.json")

        # Check if JSON file exists and set the starting frame
        self.set_starting_frame()

        # Start displaying the first frame from the desired starting frame
        self.update_video_frame()
        self.play_pause()  # Automatically start playing after the video loads

        # Set focus to the label input field initially
        self.label_input.focus_set()

    def set_starting_frame(self):
        """Set the starting frame based on the last event in the JSON file if it exists."""
        if os.path.exists(self.annotation_file_path):
            with open(self.annotation_file_path, 'r') as json_file:
                data = json.load(json_file)
                if data["annotations"]:
                    last_annotation = data["annotations"][-1]
                    self.current_frame = int(last_annotation["position"])
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        else:
            self.current_frame = 0  # Start from the beginning if no JSON file

    def update_video_frame(self):
        if self.is_playing or self.current_frame == 0:  # Ensure the first frame is displayed
            self.show_current_frame()

        # Call this method again to keep updating the frames
        self.root.after(30, self.update_video_frame)

    def show_current_frame(self):
        """Display the current frame immediately on the video panel."""
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2_image = cv2.resize(cv2_image, (self.target_width, self.target_height))

            for annotation in self.annotations:
                if annotation["position"] == self.current_frame:
                    cv2.putText(cv2_image, f"{annotation['label']} - {annotation['team']}",
                                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            img = Image.fromarray(cv2_image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_panel.imgtk = imgtk
            self.video_panel.config(image=imgtk)

    def play_pause(self):
        self.is_playing = not self.is_playing

    def forward_10(self):
        new_frame = self.current_frame + int(self.fps)
        if new_frame < self.frame_count:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
            self.current_frame = new_frame
            self.show_current_frame()  # Show frame immediately after moving forward

    def forward_1(self):
        new_frame = self.current_frame + 1
        if new_frame < self.frame_count:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
            self.current_frame = new_frame
            self.show_current_frame()  # Show frame immediately after moving forward

    def backward_10(self):
        new_frame = self.current_frame - int(self.fps)
        if new_frame >= 0:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
            self.current_frame = new_frame
            self.show_current_frame()  # Show frame immediately after moving backward

    def backward_1(self):
        new_frame = self.current_frame - 3
        if new_frame >= 0:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
            self.current_frame = new_frame
            self.show_current_frame()  # Show frame immediately after moving backward

    def annotate_frame(self):
        # Get the current game time in MM:SS format
        total_seconds = int(self.current_frame // self.fps)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        game_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        # Get label and team from input fields
        label = self.label_input.get()
        team = self.team_input.get()

        if not label or not team:
            print("Please enter both label and team.")
            return

        # Annotation details
        annotation = {
            "gameTime": game_time,
            "label": label,
            "position": str(self.current_frame),
            "team": team,
            "visibility": "visible"
        }

        # Add annotation to list
        self.annotations.append(annotation)
        print(f"Annotation added at frame {self.current_frame}: {annotation}")

        # Save annotations to JSON file
        self.save_annotations()

    def save_annotations(self):
        # Prepare the data to save
        data = {
            "UrlLocal": self.url_local,
            "UrlYoutube": "",
            "annotations": []
        }

        # Check if the JSON file already exists
        if os.path.exists(self.annotation_file_path):
            # If it exists, load the existing annotations
            with open(self.annotation_file_path, 'r') as json_file:
                existing_data = json.load(json_file)
                data["annotations"] = existing_data["annotations"]

        # Add new annotations to the list
        data["annotations"].extend(self.annotations)

        # Save annotations to the JSON file
        with open(self.annotation_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        # Clear the annotations list after saving
        self.annotations.clear()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoAnnotatorApp(root)
    root.mainloop()
