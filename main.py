import customtkinter as ctk
import os
import ffmpeg
import threading
from tkinter import filedialog



class App(ctk.CTk):
    def __init__(self):
        global name_without_ext
        global file_path
        global file_name
        global file_type

        print("Setup")

        print("FFMPEG PATH:", ffmpeg.__file__)

        # window stuff
        super().__init__()
        self.geometry("600x500")
        self.title("OpenMake Convert 0.0")
        #self.iconbitmap("./logo.ico")

        self.update_idletasks()
        width = self.winfo_width()
        self.bind("<Configure>")

        # widgets
        self.button = ctk.CTkButton(self, command=self.choose_file, text="Choose File", width=(width-40), corner_radius=25)
        self.button.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.label = ctk.CTkLabel(self, text="no file selected")
        self.label.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.label_source = ctk.CTkLabel(self, text="source type none")
        self.label_source.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.convert_button = ctk.CTkButton(self, command=self.convert, text="Convert", width=(width-40), corner_radius=25, state="disabled")
        self.convert_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # other configuration stuff i don't understand
        self.grid_columnconfigure(0, weight=1)

    def choose_file(self):
        global name_without_ext
        global file_path
        global file_name
        global file_type

        file_path = filedialog.askopenfilename(
            parent=self,
            title="Select a File",
            filetypes=[("All Files", "*.*")]
        )

        # Update the UI if a file was chosen
        if file_path:
            file_name = os.path.basename(file_path)
            name_without_ext, file_extension = os.path.splitext(file_name)
            file_type = file_extension.replace(".", "")
            self.label.configure(text=f"selected file \n{file_path}")
            self.label_source.configure(text=f"source type .{file_type}")
            print("\nFILE CHOSEN:")
            print(f"path: {file_path}\nname: {file_name}\ntype: {file_type}\n")
            self.convert_button.configure(state="normal")

    def convert(self):
        global file_type
        global file_path
        global file_name
        global name_without_ext

        def ffmpeg_process():
            export_type = ""
            if file_type == "mp4":
                export_type = "mov"
            elif file_type == "mov":
                export_type = "mp4"

            (
                ffmpeg
                .input(file_path)
                .output(f"{name_without_ext}.{export_type}")
                .run()
            )

            # WHEN CONVERSION IS DONE
            popup.destroy()
            print("Conversion complete!")

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

app = App()
app.mainloop()