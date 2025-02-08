import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import wave
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

WAVE_TYPES = {
    "Sine Wave": np.sin,
    "Square Wave": lambda x: np.sign(np.sin(x)),
    "Triangle Wave": lambda x: 2 * np.abs(2 * (x / (2 * np.pi) % 1) - 1) - 1,
    "Sawtooth Wave": lambda x: 2 * (x / (2 * np.pi) % 1) - 1
}

class AudioGeneratorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Audio Wave Generator v1.0")
        

        self.current_signal = None
        self.is_playing = False
        
        self.create_widgets()
        
        self.master.geometry("800x600")
        
    def create_widgets(self):

        control_frame = ttk.Frame(self.master, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Label(control_frame, text="Frequency (Hz):").grid(row=0, column=0, padx=5)
        self.freq_entry = ttk.Entry(control_frame)
        self.freq_entry.grid(row=0, column=1, padx=5)
        

        ttk.Label(control_frame, text="Duration (seconds):").grid(row=0, column=2, padx=5)
        self.duration_entry = ttk.Entry(control_frame)
        self.duration_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(control_frame, text="Wave Type:").grid(row=0, column=4, padx=5)
        self.wave_type = tk.StringVar()
        self.wave_combobox = ttk.Combobox(control_frame, textvariable=self.wave_type, 
                                        values=list(WAVE_TYPES.keys()))
        self.wave_combobox.current(0)
        self.wave_combobox.grid(row=0, column=5, padx=5)
        

        ttk.Label(control_frame, text="Volume Level:").grid(row=1, column=0, padx=5)
        self.volume_scale = ttk.Scale(control_frame, from_=0.1, to=1.0, length=150)
        self.volume_scale.set(0.5)
        self.volume_scale.grid(row=1, column=1, padx=5)
        

        self.start_btn = ttk.Button(control_frame, text="Start", command=self.start_audio)
        self.start_btn.grid(row=1, column=2, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_audio, state=tk.DISABLED)
        self.stop_btn.grid(row=1, column=3, padx=5)
        
        self.save_btn = ttk.Button(control_frame, text="Save", command=self.save_audio)
        self.save_btn.grid(row=1, column=4, padx=5)
        

        self.figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
    def generate_wave(self):
        try:
            frequency = float(self.freq_entry.get())
            duration = float(self.duration_entry.get())
            wave_type = self.wave_type.get()
            volume = self.volume_scale.get()
            
            t = np.linspace(0, duration, int(44100 * duration), endpoint=False)
            wave_func = WAVE_TYPES[wave_type]
            
            signal = volume * wave_func(2 * np.pi * frequency * t)
            
            fade_length = int(0.05 * 44100)
            fade_in = np.linspace(0, 1, fade_length)
            fade_out = np.linspace(1, 0, fade_length)
            
            signal[:fade_length] *= fade_in
            signal[-fade_length:] *= fade_out
            
            return t, np.clip(signal, -1, 1)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid Inputs: {str(e)}")
            return None, None
    
    def update_plot(self, time_values, signal):
        self.ax.clear()
        self.ax.plot(time_values[:1000], signal[:1000], 'b')
        self.ax.set_title("Waveform")
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_ylabel("Amplitude")
        self.ax.grid(True)
        self.canvas.draw()
    
    def start_audio(self):
        time_values, signal = self.generate_wave()
        if signal is not None:
            self.current_signal = signal
            self.update_plot(time_values, signal)
            
            self.is_playing = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            sd.stop()  
            sd.play(signal, samplerate=44100)
    
    def stop_audio(self):
        self.is_playing = False
        sd.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def save_audio(self):
        if self.current_signal is None:
            messagebox.showwarning("Warning", "There is no audio data to save.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if file_path:
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(44100)
                wf.writeframes((self.current_signal * 32767).astype(np.int16).tobytes())
            messagebox.showinfo("Saved", f"The file has been saved successfully:\n {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioGeneratorApp(root)
    root.mainloop()