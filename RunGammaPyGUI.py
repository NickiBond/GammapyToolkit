import tkinter as tk
from tkinter import filedialog, ttk
import tkinter.messagebox
import subprocess
from PIL import Image, ImageTk

# --- Help messages ---
help_dict = {
    "VEGASLogFile": "Path to VEGAS Stage 6 log file. Provide if you want spectral comparison.",
    "ObjectName": "Only accept runs with this object name. Also used to determine source co-ordinates.",
    "DL3Path": "Path to the DL3 data folder. Default is './'DL3.",
    "ADir": "Directory to save the analysis output. Default is './Analysis'.",
    "RunList": "Optional file listing runs to include. If not provided all runs will be included.",
    "RunExcludeList": "Optional file listing runs to exclude. If not provided all runs will be included.",
    "FromDate": "Only accept runs after this date (yyyy-mm-ddThh:mm:ss). Default '2007-01-01T00:00:00'.",
    "ToDate": "Only accept runs before this date (yyyy-mm-ddThh:mm:ss). Default '2030-01-01T00:00:00'.",
    "OnRegionRadius": "Radius of the on region in degrees. VEGAS Default is 0.07071068 to match IRFs.",
    "EnergyAxisMin": "Minimum energy for analysis. Default 0.1 TeV.",
    "EnergyAxisMax": "Maximum energy for analysis. Default 100 TeV.",
    "EnergyAxisBins": "Number of energy bins. Default 10.",
    "IntegralFluxMinEnergy": "Minimum energy for integral flux. Default 0.2 TeV.",
    "SpectralVariabilityTimeBinFile": "Optional time bin file for spectral variability analysis.",
    "LightCurve": "Enable light curve generation (True/False). Default False.",
    "LightCurveBinDuration": "Bin duration for light curve. Default 1 day.",
    "LightCurveMinEnergy": "Minimum energy for light curve; defaults to Energy Axis Min if blank.",
    "LightCurveNSigma": "Sigma level for error computation. Default 1.",
    "LightCurveNSigmaUL": "Sigma level for upper limit computation. Default 2.",
    "LightCurveSelectionOptional": "Optional steps for light curve processing (e.g. 'all', 'ul', 'scan').",
    "LightCurveComparisonPoints": "CSV file with points for light curve comparison.",
    "LightCurveComparisonULs": "CSV file with upper limits for comparison.",
    "IncludeNearby": "Include observations of sources within 5 deg of ObjectName in the analysis. default= False",
     "SpectralModel": "Choose the spectral model: PowerLaw, LogParabola, or ExpCutoffPowerLaw.",
    "Index": "Spectral index for PowerLaw or ExpCutoffPowerLaw.",
    "Amplitude": "Amplitude at reference energy in cm^-2 s^-1 TeV^-1.",
    "Reference": "Reference energy in TeV for PowerLaw.",
    "Alpha": "Alpha parameter for LogParabola.",
    "Beta": "Beta parameter for LogParabola.",
    "E_0": "Reference energy E_0 for LogParabola or cutoff energy for ExpCutoffPowerLaw.",
    "Lambda_": "Cutoff parameter lambda for ExpCutoffPowerLaw."
}

# --- Tooltip class ---
class CreateToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.showtip)
        widget.bind("<Leave>", self.hidetip)

    def showtip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 20
        y = y + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.geometry(f"+{x}+{y}")

        label = tk.Label(
            tw, text=self.text, justify="left",
            background="#333333",       # Dark background
            foreground="white",         # Light text
            relief="solid", borderwidth=1,
            font=("tahoma", "9", "normal"), wraplength=300
        )
        label.pack(ipadx=1)

    def hidetip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# --- Browsing logic ---
def browse_folder(entry):
    path = filedialog.askdirectory()
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

def browse_file(entry):
    path = filedialog.askopenfilename()
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

# --- Script execution ---
import json
import os

def run_script():
    if entries["ObjectName"].get().strip() == "":
        tk.messagebox.showerror("Input Error", "Object Name is required.")
        return

    args = [
        "/Users/nickibond/NBvenv/bin/python",
        "/Users/nickibond/Documents/Research/Toolkit/DL3toDL5.py"
    ]

    saved_data = {}

    for key, widget in entries.items():
        value = widget.get().strip()
        saved_data[key] = value
        if value != "":
            args += [f"-{key}", value]

    # Booleans
    saved_data["LightCurve"] = lightcurve_var.get()
    args += ["-LightCurve", str(lightcurve_var.get())]
    
    saved_data["IncludeNearby"] = include_nearby_var.get()
    if include_nearby_var.get():
        args += ["-IncludeNearby"]

    # Spectral model
    saved_data["SpectralModel"] = spectral_model_var.get()
    args += ["-SpectralModel", spectral_model_var.get()]
    for key, (label, entry) in spectral_entries.items():
        val = entry.get().strip()
        saved_data[key] = val
        if val != "":
            args += [f"-{key}", val]

    # Save arguments to file
    with open("last_used_args.json", "w") as f:
        json.dump(saved_data, f, indent=2)

    subprocess.run(args, cwd="/Users/nickibond/Documents")

# --- Show help ---
def show_help():
    help_text = "\n".join([f"{k}: {v}" for k, v in help_dict.items()])
    help_win = tk.Toplevel(root)
    help_win.title("Help Information")
    help_win.geometry("600x500")
    text = tk.Text(help_win, wrap="word")
    text.insert("1.0", help_text)
    text.config(state="disabled")
    text.pack(fill="both", expand=True)
    scrollbar = ttk.Scrollbar(help_win, command=text.yview)
    scrollbar.pack(side="right", fill="y")
    text.config(yscrollcommand=scrollbar.set)

# --- Reset form ---
def reset_form():
    for entry in entries.values():
        entry.delete(0, tk.END)
    for _, entry in spectral_entries.values():
        entry.delete(0, tk.END)
    lightcurve_var.set(False)
    include_nearby_var.set(False)
    spectral_model_var.set("PowerLaw")
    update_spectral_fields()
    if os.path.exists("last_used_args.json"):
        os.remove("last_used_args.json")

# --- GUI setup ---
root = tk.Tk()
root.title("DL3 to DL5 GUI")
entries = {}

image = Image.open("/Users/nickibond/Documents/Research/Toolkit/ChatGPTGammaPyScriptLogo.png")
resized_image = image.resize((480,480), Image.LANCZOS)
logo = ImageTk.PhotoImage(resized_image)

main_container = tk.Frame(root)
main_container.pack(fill="both", expand=True)

left_frame = tk.Frame(main_container)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

right_frame = tk.Frame(main_container)
right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

logo_label = tk.Label(left_frame, image=logo)
logo_label.pack(anchor="n")

notebook = ttk.Notebook(right_frame)
notebook.pack(fill="both", expand=True)

buttons_frame = tk.Frame(right_frame)
buttons_frame.pack(side="bottom", pady=10)

# --- Add entry with tooltip ---
def add_entry(frame, label_text, key, default="", browse=False, folder=False, row=None):
    label = tk.Label(frame, text=label_text)
    entry = tk.Entry(frame, width=50)
    entry.insert(0, default)
    label.grid(row=row, column=0, sticky="e", padx=5, pady=2)
    entry.grid(row=row, column=1, pady=2, padx=2)
    if browse:
        btn = tk.Button(frame, text="Browse", command=lambda: browse_folder(entry) if folder else browse_file(entry))
        btn.grid(row=row, column=2, padx=2)
    if key in help_dict:
        CreateToolTip(entry, help_dict[key])
    entries[key] = entry

# --- Tabs ---
sections = {
    "Data Selection": {},
    "Energy Axis": {},
    "SED": {},
    "Light Curve": {}
}
frames = {}
for section in sections:
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=section)
    frames[section] = frame

# --- Data Selection tab ---
f = frames["Data Selection"]
add_entry(f, "Object Name (required)", "ObjectName", "", row=0)
include_nearby_var = tk.BooleanVar(value=False)
label = tk.Label(f, text="Include Nearby?")
label.grid(row=1, column=0, sticky="e", padx=5, pady=2)
tk.Checkbutton(f, variable=include_nearby_var).grid(row=1, column=1, sticky="w", pady=2)

add_entry(f, "DL3 Path", "DL3Path", "./DL3", browse=True, folder=True, row=2)
add_entry(f, "Analysis Output Dir", "ADir", "./Analysis", browse=True, folder=True, row=3)
add_entry(f, "Run List File", "RunList", "", browse=True, row=4)
add_entry(f, "Exclude Run List File", "RunExcludeList", "", browse=True, row=5)
add_entry(f, "From Date", "FromDate", "2007-01-01T00:00:00", row=6)
add_entry(f, "To Date", "ToDate", "2030-01-01T00:00:00", row=7)
add_entry(f, "On Region Radius (deg)", "OnRegionRadius", "0.07071068", row=8)

# --- Energy Axis tab ---
f = frames["Energy Axis"]
add_entry(f, "Energy Axis Min (TeV)", "EnergyAxisMin", "0.1", row=0)
add_entry(f, "Energy Axis Max (TeV)", "EnergyAxisMax", "100", row=1)
add_entry(f, "Energy Axis Bins", "EnergyAxisBins", "10", row=2)

# --- SED tab ---
f = frames["SED"]
add_entry(f, "VEGAS Log File", "VEGASLogFile", "", browse=True, row=0)
add_entry(f, "Integral Flux Min Energy", "IntegralFluxMinEnergy", "0.2", row=1)
add_entry(f, "Spectral Variability Time Bin File", "SpectralVariabilityTimeBinFile", "", browse=True, row=2)

# --- Light Curve tab ---
f = frames["Light Curve"]
lightcurve_var = tk.BooleanVar(value=False)
label = tk.Label(f, text="Light Curve?")
label.grid(row=0, column=0, sticky="e", padx=5, pady=2)
tk.Checkbutton(f, variable=lightcurve_var).grid(row=0, column=1, sticky="w", pady=2)
CreateToolTip(label, help_dict["LightCurve"])
add_entry(f, "LC Bin Duration (days)", "LightCurveBinDuration", "1", row=1)
add_entry(f, "LC Min Energy (TeV)", "LightCurveMinEnergy", "", row=2)
add_entry(f, "LC NSigma", "LightCurveNSigma", "1", row=3)
add_entry(f, "LC NSigma UL", "LightCurveNSigmaUL", "2", row=4)
add_entry(f, "LC Selection Optional", "LightCurveSelectionOptional", "", row=5)
add_entry(f, "LC Comparison Points (CSV)", "LightCurveComparisonPoints", "", browse=True, row=6)
add_entry(f, "LC Comparison ULs (CSV)", "LightCurveComparisonULs", "", browse=True, row=7)

# --- Spectral Model tab ---
f = ttk.Frame(notebook)
notebook.add(f, text="Spectral Model")
frames["Spectral Model"] = f

spectral_model_var = tk.StringVar(value="PowerLaw")  # Default selection

tk.Label(f, text="Spectral Model").grid(row=0, column=0, sticky="e", padx=5, pady=2)
model_menu = ttk.Combobox(f, textvariable=spectral_model_var, values=["PowerLaw", "LogParabola", "ExpCutoffPowerLaw"])
model_menu.grid(row=0, column=1, sticky="w", padx=5, pady=2)
CreateToolTip(model_menu, "Select the spectral model for SED fitting.")

spectral_entries = {}

def add_spectral_entry(label_text, key, row, default=""):
    label = tk.Label(f, text=label_text)
    entry = tk.Entry(f, width=20)
    entry.insert(0, default)
    label.grid(row=row, column=0, sticky="e", padx=5, pady=2)
    entry.grid(row=row, column=1, sticky="w", padx=5, pady=2)
    CreateToolTip(entry, help_dict.get(key, f"{label_text} for selected spectral model."))
    spectral_entries[key] = (label, entry)

# Define fields (shown conditionally based on model)
add_spectral_entry("Index", "Index", row=1)
add_spectral_entry("Amplitude", "Amplitude", row=2)
add_spectral_entry("Reference (TeV)", "Reference", row=3)

add_spectral_entry("Alpha", "Alpha", row=4)
add_spectral_entry("Beta", "Beta", row=5)
add_spectral_entry("E_0 (TeV)", "E_0", row=6)

add_spectral_entry("Lambda", "Lambda_", row=7)

def update_spectral_fields(*args):
    model = spectral_model_var.get()

    for label, entry in spectral_entries.values():
        label.grid_remove()
        entry.grid_remove()

    if model == "PowerLaw":
        for key in ["Index", "Amplitude", "Reference"]:
            spectral_entries[key][0].grid()
            spectral_entries[key][1].grid()
    elif model == "LogParabola":
        for key in ["Alpha", "Beta", "Amplitude", "E_0"]:
            spectral_entries[key][0].grid()
            spectral_entries[key][1].grid()
    elif model == "ExpCutoffPowerLaw":
        for key in ["Index", "Amplitude", "Reference", "Lambda_", "E_0"]:
            spectral_entries[key][0].grid()
            spectral_entries[key][1].grid()

# Bind dropdown change to the function
model_menu.bind("<<ComboboxSelected>>", update_spectral_fields)
update_spectral_fields()  # Initialize view


# --- Help menu ---
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Show Help", command=show_help)

tk.Button(buttons_frame, text="Run DL3toDL5", command=run_script, bg="#4CAF50", fg="blue", padx=10, pady=5).pack(side="left", padx=10)
tk.Button(buttons_frame, text="Help", command=show_help, bg="#2196F3", fg="red", padx=10, pady=5).pack(side="left", padx=10)
tk.Button(buttons_frame, text="Reset", command=reset_form, bg="#f436c8", fg="black", padx=10, pady=5).pack(side="left", padx=10)

def load_saved_args():
    if os.path.exists("last_used_args.json"):
        with open("last_used_args.json", "r") as f:
            data = json.load(f)
        for key, val in data.items():
            if key in entries:
                entries[key].delete(0, tk.END)
                entries[key].insert(0, val)
            elif key == "LightCurve":
                lightcurve_var.set(val)
            elif key == "IncludeNearby":
                include_nearby_var.set(val)
            elif key == "SpectralModel":
                spectral_model_var.set(val)
                update_spectral_fields()
            elif key in spectral_entries:
                spectral_entries[key][1].delete(0, tk.END)
                spectral_entries[key][1].insert(0, val)

load_saved_args()

root.mainloop()
