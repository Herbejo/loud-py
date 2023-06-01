import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
import os
import shutil
import subprocess
import tempfile
import soundfile as sf
import configparser
import json
import pandas as pd
import numpy as np
from math import log10
import ctypes
import platform
import threading
import time



class audio_item:
    #loudness tagets
    target_max_true_peak = 0
    target_integrated_loudness = 0
    target_loudness_range = 0
    #compressor settings
    lra_threshold = 3.8
    threshold = -18
    attack = 4
    release = 250
    ratio = 4.5
    def __init__(self, file_path, current_file):
        self.input_file = file_path
        self.current_file = current_file
        self.max_true_peak = 0
        self.integrated_loudness = 0
        self.loudness_range = 0
        self.relative_threshold = 0
        self.loudness_offset = 0
        self.rms = 0
        self.correlation = 0


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings Window")
        self.transient(root)

        target_i = tk.StringVar(self, config["loudness_targets"]["target_I"])
        target_lra = tk.StringVar(self, config["loudness_targets"]["target_LRA"])
        target_tp = tk.StringVar(self, config["loudness_targets"]["target_TP"])
        mono = tk.StringVar(self, config["mono"]["threshold"])
        lra_threshold = tk.StringVar(self, config["compressor"]["lra_threshold"])
        attack = tk.StringVar(self, config["compressor"]["attack"])
        release = tk.StringVar(self, config["compressor"]["release"])
        ratio = tk.StringVar(self, config["compressor"]["ratio"])

        self.grid_columnconfigure(0, weight=1)  # Make column 0 expand to fill available space
        self.grid_columnconfigure(1, weight=1)

        self.dirs_labelFrame = tk.LabelFrame(self, text="Default Directories")
        self.dirs_labelFrame.grid(column=0, row=0, sticky=tk.N+tk.S+tk.E+tk.W, columnspan=2)

        self.input_labelframe = tk.LabelFrame(self.dirs_labelFrame, text="Input Directory")
        self.input_labelframe.grid(column=0, row=0, sticky=tk.N+tk.S+tk.E+tk.W)

        self.input_dir_button = tk.Button(self.input_labelframe, text="Select Directory", command=self.select_input_dir)
        self.input_dir_button.grid(column=0, row=0, sticky=tk.E+tk.W, padx=5, pady=5)

        self.input_dir_label_frame = tk.LabelFrame(self.input_labelframe, bg="white")
        self.input_dir_label_frame.grid(column=1, row=0, sticky=tk.N+tk.S+tk.E+tk.W, padx=5, pady=5)

        self.input_dir_label = tk.Label(self.input_dir_label_frame, text=config["default"]["input_path"], bg="white")
        self.input_dir_label.grid(column=0, row=0, sticky=tk.E+tk.W)

        self.output_labelframe = tk.LabelFrame(self.dirs_labelFrame, text="Output Directory")
        self.output_labelframe.grid(column=0, row=1, sticky=tk.N+tk.S+tk.E+tk.W)

        self.output_dir_button = tk.Button(self.output_labelframe, text="Select Directory", command=self.select_output_dir)
        self.output_dir_button.grid(column=0, row=1, sticky=tk.E+tk.W, padx=5, pady=5)

        self.output_dir_label_frame = tk.LabelFrame(self.output_labelframe, bg="white")
        self.output_dir_label_frame.grid(column=1, row=1, sticky=tk.N+tk.S+tk.E+tk.W, padx=5, pady=5)

        self.output_dir_label = tk.Label(self.output_dir_label_frame, text=config["default"]["output_path"], bg="white")
        self.output_dir_label.grid(column=0, row=1, sticky=tk.W)

        self.temp_labelframe = tk.LabelFrame(self.dirs_labelFrame, text="Temporary Directory")
        self.temp_labelframe.grid(column=0, row=2, sticky=tk.N+tk.S+tk.E+tk.W)

        self.temp_dir_button = tk.Button(self.temp_labelframe, text="Select Directory", command=self.select_temp_dir)
        self.temp_dir_button.grid(column=0, row=1, sticky=tk.E+tk.W, padx=5, pady=5)

        self.temp_dir_label_frame = tk.LabelFrame(self.temp_labelframe, bg="white")
        self.temp_dir_label_frame.grid(column=1, row=1, sticky=tk.N+tk.S+tk.E+tk.W, padx=5, pady=5)

        self.temp_dir_label = tk.Label(self.temp_dir_label_frame, text=config["default"]["temp_folder"], bg="white")
        self.temp_dir_label.grid(column=0, row=1, sticky=tk.W)

        self.targets_labelframe = tk.LabelFrame(self, text="Loudness Targets")
        self.targets_labelframe.grid(column=0, row=1, sticky=tk.N+tk.S+tk.E+tk.W, columnspan=2)

        self.target_i_label = tk.Label(self.targets_labelframe, text="Target Integrated Loudness")
        self.target_i_label.grid(column=0, row=0, sticky=tk.W)

        self.target_i_entry = tk.Entry(self.targets_labelframe, textvariable=target_i)
        self.target_i_entry.grid(column=1, row=0, sticky=tk.W)

        self.target_lra_label = tk.Label(self.targets_labelframe, text="Target Loudness Range")
        self.target_lra_label.grid(column=0, row=1, sticky=tk.W)

        self.target_lra_entry = tk.Entry(self.targets_labelframe, textvariable=target_lra)
        self.target_lra_entry.grid(column=1, row=1, sticky=tk.W)

        self.target_tp_label = tk.Label(self.targets_labelframe, text="Target True Peak")
        self.target_tp_label.grid(column=0, row=2, sticky=tk.W)

        self.target_tp_entry = tk.Entry(self.targets_labelframe, textvariable=target_tp)
        self.target_tp_entry.grid(column=1, row=2, sticky=tk.W)

        self.stereo_labelframe = tk.LabelFrame(self, text="Stereo Settings")
        self.stereo_labelframe.grid(column=0, row=2, sticky=tk.N+tk.S+tk.E+tk.W, columnspan=2)

        self.mono_label = tk.Label(self.stereo_labelframe, text="Mono Threshold")
        self.mono_label.grid(column=0, row=0, sticky=tk.W+tk.E)

        self.mono_entry = tk.Entry(self.stereo_labelframe, textvariable=mono)
        self.mono_entry.grid(column=1, row=0, sticky=tk.W+tk.E)

        self.compressor_labelframe = tk.LabelFrame(self, text="Compressor Settings")
        self.compressor_labelframe.grid(column=0, row=3, sticky=tk.N+tk.S+tk.E+tk.W, columnspan=2)

        self.lra_threshold_label = tk.Label(self.compressor_labelframe, text="Maximum Loudness Range")
        self.lra_threshold_label.grid(column=0, row=0, sticky=tk.W)
        self.lra_threshold_entry = tk.Entry(self.compressor_labelframe, textvariable=lra_threshold)
        self.lra_threshold_entry.grid(column=1, row=0, sticky=tk.W)

        self.attack_label = tk.Label(self.compressor_labelframe, text="Attack Time (ms)")
        self.attack_label.grid(column=0, row=1, sticky=tk.W)
        self.attack_entry = tk.Entry(self.compressor_labelframe, textvariable=attack)
        self.attack_entry.grid(column=1, row=1, sticky=tk.W)

        self.release_label = tk.Label(self.compressor_labelframe, text="Release Time (ms)")
        self.release_label.grid(column=0, row=2, sticky=tk.W)
        self.release_entry = tk.Entry(self.compressor_labelframe, textvariable=release)
        self.release_entry.grid(column=1, row=2, sticky=tk.W)

        self.ratio_label = tk.Label(self.compressor_labelframe, text="Ratio (n:1)")
        self.ratio_label.grid(column=0, row=3, sticky=tk.W)
        self.ratio_entry = tk.Entry(self.compressor_labelframe, textvariable=ratio)
        self.ratio_entry.grid(column=1, row=3, sticky=tk.W)

        self.save_button = tk.Button(self, text="Save", command=self.save_settings)
        self.save_button.grid(column=0, row=4, sticky=tk.W+tk.E)

        self.close_button = tk.Button(self, text="Close", command=self.close_window)
        self.close_button.grid(column=1, row=4, sticky=tk.W+tk.E)

    def select_input_dir(self):
        config["default"]["input_path"] = tk.filedialog.askdirectory()
        self.input_dir_label.config(text=config["default"]["input_path"])

    def select_output_dir(self):
        config["default"]["output_path"] = tk.filedialog.askdirectory()
        self.output_dir_label.config(text=config["default"]["output_path"])

    def select_temp_dir(self):
        config["default"]["temp_folder"] = tk.filedialog.askdirectory()
        self.temp_dir_label.config(text=config["default"]["temp_folder"])

    def save_settings(self):
        config["loudness_targets"]["target_I"] = self.target_i_entry.get()
        config["loudness_targets"]["target_LRA"] = self.target_lra_entry.get()
        config["loudness_targets"]["target_TP"] = self.target_tp_entry.get()
        config["mono"]["threshold"] = self.mono_entry.get()
        config["compressor"]["lra_threshold"] = self.lra_threshold_entry.get()
        config["compressor"]["attack"] = self.attack_entry.get()
        config["compressor"]["release"] = self.release_entry.get()
        config["compressor"]["ratio"] = self.ratio_entry.get()

        with open("config.ini", "w") as config_file:
            config.write(config_file)
            
        self.close_window()

    def close_window(self):

        self.destroy()


class MainApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.menu = tk.Menu(self, background='blue', fg='white')

        self.fileMenu = tk.Menu(self.menu, tearoff=False)
        self.fileMenu.add_command(label="Settings", command=self.open_settings_window)
        self.fileMenu.add_command(label="Exit", command=root.destroy)
        self.menu.add_cascade(label="File", menu=self.fileMenu)
        self.parent.config(menu=self.menu)

        #make the gui 
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=2)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=6)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=2)


        
        self.input_dir_labelframe = tk.LabelFrame(self, bg="white")
        self.input_dir_labelframe.grid(column=0, row=0, sticky=tk.N+tk.S+tk.E+tk.W, columnspan=3, padx=5, pady=5)
        self.input_dir_label = tk.Label(self.input_dir_labelframe, text=config["default"]["input_path"], bg="white")
        self.input_dir_label.grid(column=0, row=0, sticky=tk.W)
        self.input_dir_button = tk.Button(self, text="Select input Directory", command=self.select_input_dir) #replace command
        self.input_dir_button.grid(column=3, row=0, sticky=tk.E+tk.W, padx=5, pady=5)

        self.output_dir_labelframe = tk.LabelFrame(self, bg="white")
        self.output_dir_labelframe.grid(column=0, row=1, sticky=tk.N+tk.S+tk.E+tk.W, columnspan=3, padx=5, pady=5)
        self.output_dir_label = tk.Label(self.output_dir_labelframe, text=config["default"]["output_path"], bg="white")
        self.output_dir_label.grid(column=0, row=1, sticky=tk.W)
        self.output_dir_button = tk.Button(self, text="Select output Directory", command=self.select_output_dir) #replace command
        self.output_dir_button.grid(column=3, row=1, sticky=tk.E+tk.W, padx=5, pady=5)

        self.status_text = scrolledtext.ScrolledText(self, wrap = tk.WORD, font = ("Tahoma",9),)
        self.status_text.grid(column=0, row=2, sticky=tk.N+tk.S+tk.E+tk.W, columnspan=4, padx=5, pady=5)
        self.status_text.config(state="disabled")

        self.process_files_button = tk.Button(self, text="Start Process", command=self.start_process_thread)
        self.process_files_button.grid(column=0, row=3, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)

        self.find_files_button = tk.Button(self, text="Stop Process", command=self.stop_processing)
        self.find_files_button.grid(column=2, row=3, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)

        self.load_config()

    def start_process_thread(self):
        global processing
        if config["default"]["input_path"] != config["default"]["output_path"]:
            processing = True
            threading.Thread(target=self.process_files).start()
        else:
            tk.messagebox.showerror(title="Error", message="Input and Output directories cannot match")

    def stop_processing(self):
        global processing
        
        if processing:
            self.status_print("Stopping Process \n")
        processing = False


    def __del__(self): ##put all cleanup stuff here
        self.remove_temp_files()


    def open_settings_window(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.mainloop()

    def select_input_dir(self):
        config["default"]["input_path"] = tk.filedialog.askdirectory()
        self.input_dir_label.config(text=config["default"]["input_path"])
        

    def select_output_dir(self):
        config["default"]["output_path"] = tk.filedialog.askdirectory()
        self.output_dir_label.config(text=config["default"]["output_path"])

    def find_files(self):
        global input_files
        
        #get every file in the input dir and try to convert it to a wav
        #if it is a wav retun the path of it in the temp dir (i just covert every file to a wav, wav to wav is very quick)
        #add file to input_files, including temp name 
        input_dir_files = set(os.listdir(config["default"]["input_path"]))
        for file in input_dir_files:
            input_file = os.path.join(config["default"]["input_path"], file).replace("\\", "/")
            wav_file = self.try_convert_to_wav(input_file, self.get_temp_filename())
            if wav_file:
                input_files.append(audio_item(input_file, wav_file))
        
        self.status_print( "Found " + str(len(input_files)) + " files to process \n")

    def process_files(self):
        global input_files

        while processing:
            self.status_print("Scanning for Files to Process \n")
            self.find_files()
            files_to_process = len(input_files)
            for i in input_files:
                if not processing:
                    self.status_print("process Stopped \n")
                    break
                self.status_print(str(files_to_process) + " files to process \n")
                self.status_print("Processing " + i.input_file + "\n")
                self.get_audio_stats(i)
                self.fix_stereo(i)
                self.fix_dynamics(i)
                self.normalise(i)


                print(i.input_file)
                print("True Peak: " + str(i.max_true_peak))
                print("Intergrated Loudness: " + str(i.integrated_loudness))
                print("Loudness Range: " + str(i.loudness_range))
                print("Threshold: " + str(i.relative_threshold))
                print("RMS: " + str(i.rms))
                print("Correlation: " + str(i.correlation))
                os.remove(i.input_file)
                #input_files.remove(i)
                files_to_process = files_to_process - 1
            #self.remove_temp_files()
            input_files = []
            print("sleeping")
            time.sleep(10)


                

        #delete process list
        
    def load_config(self):
        #loudness targets
        audio_item.target_integrated_loudness = config["loudness_targets"]["target_I"]
        audio_item.target_loudness_range = config["loudness_targets"]["target_LRA"]
        audio_item.target_max_true_peak = config["loudness_targets"]["target_TP"]
        #compressor settings
        audio_item.lra_threshold = config['compressor']['lra_threshold']
        audio_item.threshold = config['compressor']['threshold']
        audio_item.attack = config['compressor']['attack']
        audio_item.release = config['compressor']['release']
        audio_item.ratio = config['compressor']['ratio']
        #set tagets in audio_items

    def get_audio_stats(self, input): # gets all stats from file, hopefuly only opening the file twice 

        command = 'ffmpeg -i "'+ input.current_file +'" -af loudnorm=print_format=json -f null -'
        print(command)
        mesure = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
        product = "\n".join(mesure.communicate()[-1].decode("UTF-8").split("\n")[-13:-1])
        lounness_data = json.loads(product)

        data, _ = sf.read(input.current_file, always_2d=True)
        d = data.astype(float)
        rms = np.sqrt(np.mean(d ** 2))
        rms_db = 20 * np.log10(rms)

        if data.shape[1] == 1:
            cr = 1
        df = pd.DataFrame(data, columns =['ch1', 'ch2'])
        cr = df.corr(method='pearson')._get_value(0, 1,takeable = True)

        input.integrated_loudness = lounness_data["input_i"] 
        input.loudness_range = lounness_data["input_lra"]
        input.relative_threshold = lounness_data["input_thresh"]
        input.max_true_peak = lounness_data["input_tp"]
        input.loudness_offset = lounness_data["target_offset"]
        input.rms = rms_db
        input.correlation = cr
    
    def run_ffmpeg(self, input, af_options, output_file):
        #get new temp file
        #run command
        #change currant file to temp file 
        
        command = (f'ffmpeg -i "{input.current_file}" -af {af_options} -f wav -y "{output_file}" -loglevel quiet')
        print(command)
        try:
            subprocess.run(command, check=True)
            input.current_file = output_file
        except subprocess.CalledProcessError:
            self.status_print("ffmpeg error")
            pass
    
    def fix_stereo(self, input):
        # if the file is split mono 
        mono_thresh = float( config["mono"]["threshold"])
        if float(input.correlation) < mono_thresh and float(input.correlation) > -0.3 :
            command = "pan=stereo|c0<c0+c1|c1<c0+c1"
            output_file = self.get_temp_filename()
            self.run_ffmpeg(input, command, output_file)
            self.get_audio_stats(input) #loudness changes after mono-ing
        #polarity correction
        elif float(input.correlation) <= -0.3:
            command = "pan=stereo|c0<c0|c1=-1*c1"
            output_file = self.get_temp_filename()
            self.run_ffmpeg(input, command, output_file)
        else:
            
            pass


    def fix_dynamics(self, input):

        while float(input.loudness_range) >= float(input.lra_threshold):
            #do thecompression here
            thresh = 10**(int(float(input.rms))/20) 
            if thresh >= 0.00097563 and thresh <= 1: #make sure the theshold isnt to low or high
                command = (f"acompressor=threshold={str(thresh)}:ratio={input.ratio}:attack={input.attack}:release={input.release}:detection=peak")
                output_file = self.get_temp_filename()
                self.run_ffmpeg(input, command, output_file)
                self.get_audio_stats(input)
            else:
                print('thrshold out of range, audio file could be silent')
    
    def normalise(self, input):
        #make output file name
        #make command
        #process file
        output_folder = config['default']['output_path']
        head, output_file_name = os.path.split(input.input_file)
        output_file_name, ext = os.path.splitext(output_file_name)
        output_file = os.path.join(output_folder, output_file_name + '.wav').replace("\\", "/")
        command = (f"loudnorm=I={input.target_integrated_loudness}:TP={input.target_max_true_peak}:LRA={input.target_loudness_range}:measured_I={input.integrated_loudness}:measured_TP={input.max_true_peak}:measured_LRA={input.loudness_range}:measured_thresh={input.relative_threshold}:offset={input.loudness_offset}:linear=false")
        self.run_ffmpeg(input, command, output_file)


    def get_temp_filename(self):
        temp_folder = config['default']['temp_folder']
        while True:
            path = os.path.join(temp_folder, next(tempfile._get_candidate_names()) + '.wav').replace("\\", "/")
            if not os.path.exists(path):
                return path
    
    def try_convert_to_wav(self, file_path, output_file):
        command = f'ffmpeg -i "{file_path}" -y "{output_file}" -loglevel quiet'
        print(command)
        try:
            subprocess.run(command, check=True)
            return output_file
        except subprocess.CalledProcessError:
            return None

    def status_print(self, text):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, str(text))
        self.status_text.config(state="disabled")
        self.status_text.see(tk.END)



    def remove_temp_files(self):
        with os.scandir(config['default']['temp_folder']) as entries:
            for entry in entries:
                if entry.is_dir() and not entry.is_symlink():
                    shutil.rmtree(entry.path)
                else:
                    os.remove(entry.path)


input_files = [] 
processing = False


def make_dpi_aware(): #this needs to be somewhere to make it look nice
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
        ctypes.windll.user32.SetProcessDPIAware()
make_dpi_aware()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    root = tk.Tk()
    root.title("Loudness Processor")
    MainApp(root).pack(side="top", fill="both", expand=True)
    root.mainloop()



#--------------todo-------------------------
# - comment it all 
# - lots of error handeling 
# - add out of phase threshold to settlings 
