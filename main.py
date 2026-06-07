from multiprocessing.forkserver import read_signed

import customtkinter as ctk
import os
import ffmpeg
import threading
from tkinter import filedialog
import webbrowser
import pathlib
from pathlib import Path
import sys
import subprocess
import time

class App(ctk.CTk):
    def __init__(self):
        global name_without_ext
        global file_path
        global file_name
        global file_type
        global conversion_types

        conversion_types = ["Choose a file to get options"]
        print("Setup")
        print("FFMPEG PATH:", ffmpeg.__file__)

        # window stuff
        super().__init__()
        self.geometry("600x250")
        self.title("OpenMake Convert beta 0.2.0")
        #self.iconbitmap("./logo.ico")

        self.update_idletasks()
        width = self.winfo_width()
        self.bind("<Configure>")

        # widgets
        self.file = ctk.CTkEntry(self, width=500, placeholder_text="Source File")
        self.file.grid(row=0, column=0, padx=5, pady=10, columnspan=1, sticky="ew")

        self.button = ctk.CTkButton(self, command=self.choose_file, text="Browse", width=(width-40), corner_radius=25)
        self.button.grid(row=0, column=1, padx=5, pady=10, columnspan=1, sticky="ew")

        self.label_source = ctk.CTkLabel(self, text="source type none")
        self.label_source.grid(row=2, column=0, padx=5, pady=10, sticky="ew")

        self.optionmenu = ctk.CTkOptionMenu(self, values=conversion_types, width=60)
        self.optionmenu.grid(row=2, column=1, columnspan=1, padx=5, pady=10, sticky="ew")

        self.convert_button = ctk.CTkButton(self, command=self.convert, text="Convert", width=(width-40), corner_radius=25, state="disabled")
        self.convert_button.grid(row=4, column=0, padx=5, pady=10, columnspan=2, sticky="ew")

        # other configuration stuff i don't understand
        self.grid_columnconfigure(0, weight=1)

        # uncomment line below if making a build from a pr or a build before its ready for release
        # self.build_popup(build_name="test", release="0.2.0")


    def build_popup(self, message="You are running an early dev build!", build_name="dev", release="0.2.0"):
        def open_wiki(page):
            webbrowser.open(f"https://github.com/Reclips0/Convert/wiki/{page}")

        # Create the popup window
        popup = ctk.CTkToplevel(self)
        popup.title("Warning")
        popup.geometry("300x300")
        popup.attributes("-topmost", True)

        label = ctk.CTkLabel(popup, text=f"{message}")
        label.pack(pady=20, padx=20)
        labelb = ctk.CTkLabel(popup, text=f"You are using {build_name}")
        labelb.pack(pady=20, padx=20)
        close_button = ctk.CTkButton(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=10)
        wiki_button = ctk.CTkButton(popup, text="Learn More", command=lambda: open_wiki("dev-builds"))
        wiki_button.pack(pady=10)
        patch_button = ctk.CTkButton(popup, text="Read patch notes", command=lambda: webbrowser.open(f"https://github.com/Reclips0/Convert/releases/tag/{release}"))
        patch_button.pack(pady=10)

    def error(self, message="An unknown error occurred", err_code="9x99"):
        def open_wiki(page):
            webbrowser.open(f"https://github.com/Reclips0/Convert/wiki/{page}")

        # Create the popup window
        popup = ctk.CTkToplevel(self)
        popup.title("Error")
        popup.geometry("300x300")
        popup.attributes("-topmost", True)

        label = ctk.CTkLabel(popup, text=f"Error: {message}")
        label.pack(pady=20, padx=20)
        labelb = ctk.CTkLabel(popup, text=f"Function resulted with code {err_code}")
        labelb.pack(pady=20, padx=20)
        close_button = ctk.CTkButton(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=10)
        wiki_button = ctk.CTkButton(popup, text="Check wiki for solutions", command=lambda: open_wiki(err_code))
        wiki_button.pack(pady=10)

    def choose_file(self):
        global name_without_ext
        global file_path
        global file_name
        global file_type

        file_path = filedialog.askopenfilename(
            parent=self,
            title="Select a File",
            filetypes=[
                ("Supported Files", ".mp4 .mp3 .mov .avi .mkv .webm .jpeg .jpg .png .webp .aac .wav .flac .m4a"),
                ("Images", ".jpeg .jpg .png .webp"),
                ("Audio", ".mp3 .aac .wav .flac .m4a"),
                ("Video", ".mp4 .mov .avu .mkv .webm"),
                ("All Files", "*.*")]
        )

        # Update the UI if a file was chosen
        if file_path:
            file_name = os.path.basename(file_path)
            name_without_ext, file_extension = os.path.splitext(file_name)
            file_type = file_extension.replace(".", "")
            # self.file.configure(textvariable=f"selected file \n{file_path}")
            self.file.delete(0, "end")
            self.file.insert(0, file_path)
            self.label_source.configure(text=f"source type .{file_type}")
            print("\nFILE CHOSEN:")
            print(f"path: {file_path}\nname: {file_name}\ntype: {file_type}\n")
            self.convert_button.configure(state="normal")
            self.available_types()

    def convert(self):
        result_type = self.optionmenu.get()
        print(result_type)

        if result_type != "select resulting file type" and result_type != "Choose a file to get options":
            global file_type
            global file_path
            global file_name
            global name_without_ext

            if Path(file_path).is_file():
                print("file exists")
            else:
                self.error(message="The file chosen does not exist", err_code="0x20")
                return

            def ffmpeg_process():
                try:
                    (
                        ffmpeg
                        .input(file_path)
                        .output(f"{name_without_ext}.{result_type}")
                        .run()
                    )

                    popup.after(0, popup.destroy)
                    print("Conversion complete!")
                except ffmpeg.Error:
                    popup.destroy()
                    self.error(message="FFmpeg encountered a problem", err_code="1x20")
                except PermissionError:
                    popup.destroy()
                    self.error(message="You do not have permission to execute this file", err_code="0x21")
                except:
                    popup.destroy()
                    self.error(message="An unknown error occurred", err_code="2x21")

            conversion_thread = threading.Thread(target=ffmpeg_process)

            print("Converting window opening...")

            # Create the popup window
            popup = ctk.CTkToplevel(self)
            popup.title("Popup Window")
            popup.geometry("300x200")
            popup.attributes("-topmost", True)

            label = ctk.CTkLabel(popup, text=f"Converting...")
            label.pack(pady=20, padx=20)
            label = ctk.CTkLabel(popup, text=f"To cancel, close cmd popup.")
            label.pack(pady=20, padx=20)

            conversion_thread.start()
        else:
            self.error(message="You must choose a result file type", err_code="2x20")



    def available_types(self):
        global file_type
        global conversion_types

        if file_type == "mp4" or file_type == "mov" or file_type == "avi" or file_type == "mkv" or file_type == "webm":
            conversion_types = ["mp4", "mov", "avi", "mkv", "webm"]
        elif file_type == "jpeg" or file_type == "jpg" or file_type == "png" or file_type == "webp":
            conversion_types = ["jpg", "png", "webp", "gif"]
        elif file_type == "mp3" or file_type == "aac" or file_type == "wav" or file_type == "flac" or file_type == "m4a":
            conversion_types = ["mp3", "aac", "wav", "flac", "m4a"]

        self.optionmenu.configure(values=conversion_types)
        self.optionmenu.set("select resulting file type")

app = App()
app.mainloop()
