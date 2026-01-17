import tkinter as tk
from tkinter import filedialog, ttk
import tkinter.messagebox
import subprocess
from PIL import Image, ImageTk
import json
import os
import threading

# --- Help messages ---
help_dict = {
    "VEGASLogFile": "Path to VEGAS Stage 6 log file. Provide if you want spectral comparison.",
    "ObjectName": "Only accept runs with this object name. Also used to determine source co-ordinates.",
    "DL3Path": "Path to the DL3 data folder. Default is './DL3'.",
    "ADir": "Directory to save the analysis output. Default is './Analysis'.",
    "RunList": "Optional text file listing runs to include. If not provided all runs will be included.",
    "RunExcludeList": "Optional text file listing runs to exclude. If not provided all runs will be included.",
    "FromDate": "Only accept runs after this date (yyyy-mm-ddThh:mm:ss). Default '2007-01-01T00:00:00'.",
    "ToDate": "Only accept runs before this date (yyyy-mm-ddThh:mm:ss). Default '2030-01-01T00:00:00'.",
    "OnRegionRadius": "Radius of the on region in degrees, default = None, in which case the radius from the IRF will be used (point-like)",
    "Debug": "Enable debug mode.",
    "BackgroundMaker": "Currently only option is 'ReflectedRegions'. Default is 'Reflected Regions'.",
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
    "SpectralModel": "Spectral model or expression of 2 models (e.g., PowerLaw, PowerLawCutOff, BrokenPowerLaw, LogParabola, SmoothBrokenPowerLaw, PowerLaw+ExpCutoff, PowerLaw+LogParabola) \n e.g. PowerLaw+ExpCutoff or PowerLaw+LogParabola and quotes around the expression. \n Default is PowerLaw.",
    "PowerLawIndex": "Spectral index for PowerLaw.",
    "PowerLawAmplitude": "Amplitude in cm^-2 s^-1 TeV^-1 for PowerLaw.",
    "PowerLawReferenceEnergy": "Reference energy in TeV for PowerLaw.",
    "PowerLawCutoffIndex": "Spectral index for ExpCutoffPowerLaw.",
    "PowerLawCutoffAmplitude": "Amplitude in cm^-2 s^-1 TeV^-1 for ExpCutoffPowerLaw.",
    "PowerLawCutoffReferenceEnergy": "Reference energy in TeV for ExpCutoffPowerLaw.",
    "PowerLawCutoffAlpha": "Alpha parameter for PowerLawCutoff.",
    "PowerLawCutoffLambda": "Cutoff parameter lambda for PowerLawCutoff.",
    "BrokenPowerLawIndex1": "Spectral index 1 for BrokenPowerLaw.",
    "BrokenPowerLawIndex2": "Spectral index 2 for BrokenPowerLaw.",
    "BrokenPowerLawEnergyBreak": "Break energy for BrokenPowerLaw.",
    "BrokenPowerLawAmplitude": "Amplitude in cm^-2 s^-1 TeV^-1 for BrokenPowerLaw.",
    "LogParabolaAmplitude": "Amplitude in cm^-2 s^-1 TeV^-1 for LogParabola.",
    "LogParabolaAlpha": "Alpha parameter for LogParabola.",
    "LogParabolaBeta": "Beta parameter for LogParabola.",
    "LogParabolaReferenceEnergy": "Reference energy for LogParabola.",
    "SmoothBrokenPowerLawIndex1": "Spectral index 1 for SmoothBrokenPowerLaw.",
    "SmoothBrokenPowerLawIndex2": "Spectral index 2 for SmoothBrokenPowerLaw.",
    "SmoothBrokenPowerLawEnergyBreak": "Break energy for SmoothBrokenPowerLaw.",
    "SmoothBrokenPowerLawAmplitude": "Amplitude in cm^-2 s^-1 TeV^-1 for SmoothBrokenPowerLaw.",
    "SmoothBrokenPowerLawReferenceEnergy": "Reference energy for SmoothBrokenPowerLaw.",
    "SmoothBrokenPowerLawBeta": "Beta parameter for SmoothBrokenPowerLaw.",
    "exclusion_csv": "Path to a CSV file containing user-defined exclusion regions. The CSV should have columns: ra (deg), dec (deg), radius (deg or with astropy unit).",
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
            tw,
            text=self.text,
            justify="left",
            background="#333333",  # Dark background
            foreground="white",  # Light text
            relief="solid",
            borderwidth=1,
            font=("tahoma", "9", "normal"),
            wraplength=300,
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


def load_json_config():
    """Load JSON configuration and populate form fields"""
    path = filedialog.askopenfilename(
        filetypes=[("JSON Files", "*.json")], title="Select JSON Configuration"
    )
    if not path:
        return

    try:
        with open(path, "r") as f:
            config = json.load(f)

        # Populate the form with loaded configuration
        populate_form_from_config(config)

        tk.messagebox.showinfo(
            "Success", f"Configuration loaded from {os.path.basename(path)}"
        )

    except json.JSONDecodeError:
        tk.messagebox.showerror("Error", "Invalid JSON file")
    except Exception as e:
        tk.messagebox.showerror("Error", f"Failed to load JSON: {str(e)}")


def populate_form_from_config(config):
    """Populate all form fields from a configuration dictionary"""
    # Clear existing form first
    reset_form()

    # Populate text entries
    for key, val in config.items():
        if key in entries:
            entries[key].delete(0, tk.END)
            entries[key].insert(0, str(val))
        elif key == "LightCurve":
            lightcurve_var.set(val in [True, "True", "true", 1, "1"])
        elif key == "IncludeNearby":
            include_nearby_var.set(val in [True, "True", "true", 1, "1"])
        elif key == "Debug":
            debug_mode_var.set(val in [True, "True", "true", 1, "1"])
        elif key == "SpectralModel":
            spectral_model_var.set(str(val))
        elif key == "BackgroundMaker":
            if str(val) in ["ReflectedRegions"]:  # Add more options as needed
                background_maker_var.set(str(val))

    # Update spectral fields with the loaded configuration
    update_spectral_fields(saved_args=config)

    # Populate any spectral parameters that were loaded
    for key, val in config.items():
        if key in spectral_entries:
            _, entry = spectral_entries[key]
            entry.delete(0, tk.END)
            entry.insert(0, str(val))


def save_json_config():
    """Save current configuration to a JSON file"""
    path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")],
        title="Save Configuration As",
    )
    if not path:
        return


# --- Script execution ---
def run_script():
    def run():
        try:
            status_var.set("Running script...")
            if entries["ObjectName"].get().strip() == "":
                tk.messagebox.showerror("Input Error", "Object Name is required.")
                return

            args = [
                "/Users/nickibond/NBvenv/bin/python",
                "/Users/nickibond/Documents/Research/Toolkit/DL3toDL5.py",
            ]

            saved_data = {}

            # Basic entries
            for key, widget in entries.items():
                value = widget.get().strip()
                saved_data[key] = value
                if value != "":
                    args += [f"-{key}", value]

            # Booleans
            saved_data["LightCurve"] = lightcurve_var.get()
            if lightcurve_var.get():
                args += ["-LightCurve"]

            saved_data["IncludeNearby"] = include_nearby_var.get()
            if include_nearby_var.get():
                args += ["-IncludeNearby"]

            saved_data["Debug"] = debug_mode_var.get()
            if debug_mode_var.get():
                args += ["-Debug"]

            # Spectral model(s)
            saved_data["SpectralModel"] = spectral_model_var.get()
            args += ["-SpectralModel", spectral_model_var.get()]

            saved_data["BackgroundMaker"] = background_maker_var.get()
            args += ["-BackgroundMaker", background_maker_var.get()]

            # Spectral parameters for compound models
            # Flatten spectral_entries dict: keys are compound keys like 'PowerLaw_Index', 'LogParabola_Alpha', etc.
            for key, (label, entry) in spectral_entries.items():
                val = entry.get().strip()
                saved_data[key] = val
                if val != "":
                    args += [f"-{key}", val]

            # Save to JSON for later reload
            with open("last_used_args.json", "w") as f:
                json.dump(saved_data, f, indent=2)

            # Save JSON to analysis folder so it can be reused if needed later (if something else has been run and overwritten last_used_args.json)
            os.makedirs(entries["ADir"].get(), exist_ok=True)
            with open(os.path.join(entries["ADir"].get(), "args.json"), "w") as f:
                json.dump(saved_data, f, indent=2)

            subprocess.run(args, cwd="/Users/nickibond/Documents")
            status_var.set("Finished!")
        except Exception as e:
            status_var.set(f"Error: {str(e)}")

    threading.Thread(target=run).start()


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
    for _, (label, entry) in spectral_entries.items():
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

main_container = tk.Frame(root)
main_container.pack(fill="both", expand=True)

left_frame = tk.Frame(main_container)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

right_frame = tk.Frame(main_container)
right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

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
        btn = tk.Button(
            frame,
            text="Browse",
            command=lambda: browse_folder(entry) if folder else browse_file(entry),
        )
        btn.grid(row=row, column=2, padx=2)
    if key in help_dict:
        CreateToolTip(entry, help_dict[key])
    entries[key] = entry


# --- Tabs ---
sections = {"Data Selection": {}, "Energy Axis": {}, "SED": {}, "Light Curve": {}}
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
CreateToolTip(label, help_dict["IncludeNearby"])
add_entry(f, "DL3 Path", "DL3Path", "./DL3", browse=True, folder=True, row=2)
add_entry(
    f, "Analysis Output Dir", "ADir", "./Analysis", browse=True, folder=True, row=3
)
add_entry(f, "Run List File", "RunList", "", browse=True, row=4)
add_entry(f, "Exclude Run List File", "RunExcludeList", "", browse=True, row=5)
add_entry(f, "From Date", "FromDate", "2007-01-01T00:00:00", row=6)
add_entry(f, "To Date", "ToDate", "2030-01-01T00:00:00", row=7)
add_entry(f, "On Region Radius (deg)", "OnRegionRadius", "0.07071068", row=8)
background_maker_options = ["ReflectedRegions"]
background_maker_var = tk.StringVar(value="ReflectedRegions")  # Default
tk.Label(f, text="Background Maker").grid(row=9, column=0, sticky="e", padx=5, pady=2)
background_maker_menu = tk.OptionMenu(
    f, background_maker_var, *background_maker_options
)
background_maker_menu.grid(row=9, column=1, sticky="w", padx=5, pady=2)
CreateToolTip(
    background_maker_menu,
    help_dict.get("BackgroundMaker", "Choose background estimation method."),
)
debug_mode_var = tk.BooleanVar(value=False)
label = tk.Label(f, text="Make Debug Plots?")
label.grid(row=10, column=0, sticky="e", padx=5, pady=2)
tk.Checkbutton(f, variable=debug_mode_var).grid(row=10, column=1, sticky="w", pady=2)
CreateToolTip(label, help_dict["Debug"])
add_entry(f, "User exclusion regions", "exclusion_csv", "", browse=True, row=11)
# --- Energy Axis tab ---
f = frames["Energy Axis"]
add_entry(f, "Energy Axis Min (TeV)", "EnergyAxisMin", "0.1", row=0)
add_entry(f, "Energy Axis Max (TeV)", "EnergyAxisMax", "100", row=1)
add_entry(f, "Energy Axis Bins", "EnergyAxisBins", "10", row=2)

# --- SED tab ---
f = frames["SED"]
add_entry(f, "VEGAS Log File", "VEGASLogFile", "", browse=True, row=0)
add_entry(f, "Integral Flux Min Energy", "IntegralFluxMinEnergy", "0.2", row=1)
add_entry(
    f,
    "Spectral Variability Time Bin File",
    "SpectralVariabilityTimeBinFile",
    "",
    browse=True,
    row=2,
)

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
add_entry(
    f,
    "LC Comparison Points (CSV)",
    "LightCurveComparisonPoints",
    "",
    browse=True,
    row=6,
)
add_entry(
    f, "LC Comparison ULs (CSV)", "LightCurveComparisonULs", "", browse=True, row=7
)

# --- Spectral Model tab with compound models ---
f = ttk.Frame(notebook)
notebook.add(f, text="Spectral Model")
frames["Spectral Model"] = f

spectral_model_var = tk.StringVar(value="PowerLaw")  # Default selection

tk.Label(f, text="Spectral Model (compound allowed)").grid(
    row=0, column=0, sticky="e", padx=5, pady=2
)
model_entry = tk.Entry(f, textvariable=spectral_model_var, width=30)
model_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
CreateToolTip(model_entry, help_dict["SpectralModel"])

spectral_params_frame = tk.Frame(f)
spectral_params_frame.grid(row=1, column=0, columnspan=3, sticky="w", padx=10, pady=10)

spectral_entries = {}

# Define model parameters per model type
spectral_model_parameters = {
    "PowerLaw": [
        ("Spectral Index", "PowerLawIndex"),
        ("Amplitude (cm⁻² s⁻¹ TeV⁻¹)", "PowerLawAmplitude"),
        ("Reference Energy (TeV)", "PowerLawReferenceEnergy"),
    ],
    "ExpCutoffPowerLaw": [
        ("Spectral Index", "PowerLawCutoffIndex"),
        ("Amplitude (cm⁻² s⁻¹ TeV⁻¹)", "PowerLawCutoffAmplitude"),
        ("Reference Energy (TeV)", "PowerLawCutoffReferenceEnergy"),
        ("Lambda", "PowerLawCutoffLambda"),
    ],
    "BrokenPowerLaw": [
        ("Spectral Index 1", "BrokenPowerLawIndex1"),
        ("Spectral Index 2", "BrokenPowerLawIndex2"),
        ("Break Energy (TeV)", "BrokenPowerLawEnergyBreak"),
        ("Amplitude (cm⁻² s⁻¹ TeV⁻¹)", "BrokenPowerLawAmplitude"),
    ],
    "LogParabola": [
        ("Alpha", "LogParabolaAlpha"),
        ("Beta", "LogParabolaBeta"),
        ("Reference Energy (TeV)", "LogParabolaReferenceEnergy"),
        ("Amplitude (cm⁻² s⁻¹ TeV⁻¹)", "LogParabolaAmplitude"),
    ],
    "SmoothBrokenPowerLaw": [
        ("Spectral Index 1", "SmoothBrokenPowerLawIndex1"),
        ("Spectral Index 2", "SmoothBrokenPowerLawIndex2"),
        ("Break Energy (TeV)", "SmoothBrokenPowerLawEnergyBreak"),
        ("Amplitude (cm⁻² s⁻¹ TeV⁻¹)", "SmoothBrokenPowerLawAmplitude"),
        ("Reference Energy (TeV)", "SmoothBrokenPowerLawReferenceEnergy"),
        ("Beta", "SmoothBrokenPowerLawBeta"),
    ],
}

DEFAULT_ARGS = {
    # PowerLaw
    "PowerLawIndex": 2.0,
    "PowerLawAmplitude": 1e-12,
    "PowerLawReferenceEnergy": 1.0,
    # PowerLaw with Cutoff
    "PowerLawCutOffIndex": 1.5,
    "PowerLawCutOffAmplitude": 1e-12,
    "PowerLawCutOffReferenceEnergy": 1.0,
    "PowerLawCutOffAlpha": 1.0,
    "PowerLawCutOffLambda": 0.1,
    # Broken Power Law
    "BrokenPowerLawIndex1": 2.0,
    "BrokenPowerLawIndex2": 2.0,
    "BrokenPowerLawAmplitude": 1e-12,
    "BrokenPowerLawEnergyBreak": 1.0,
    # Log Parabola
    "LogParabolaAmplitude": 1e-12,
    "LogParabolaReferenceEnergy": 10.0,
    "LogParabolaAlpha": 2.0,
    "LogParabolaBeta": 1.0,
    # Smooth Broken Power Law
    "SmoothBrokenPowerLawIndex1": 2.0,
    "SmoothBrokenPowerLawIndex2": 2.0,
    "SmoothBrokenPowerLawAmplitude": 1e-12,
    "SmoothBrokenPowerLawEnergyBreak": 1.0,
    "SmoothBrokenPowerLawReferenceEnergy": 1.0,
    "SmoothBrokenPowerLawBeta": 1.0,
}


def clear_spectral_params():
    for widget in spectral_params_frame.winfo_children():
        widget.destroy()
    spectral_entries.clear()


def update_spectral_fields(event=None, saved_args=None):
    if saved_args is None:
        saved_args = {}
    clear_spectral_params()
    models = spectral_model_var.get().strip().split("+")
    row = 0
    for model in models:
        model = model.strip()
        if model not in spectral_model_parameters:
            tk.Label(
                spectral_params_frame, text=f"Unknown model: {model}", fg="red"
            ).grid(row=row, column=0, sticky="w")
            row += 1
            continue
        tk.Label(
            spectral_params_frame,
            text=f"{model} parameters:",
            font=("Helvetica", 10, "bold"),
        ).grid(row=row, column=0, sticky="w", pady=(10, 2))
        row += 1
        for param_label, param_key in spectral_model_parameters[model]:
            label = tk.Label(spectral_params_frame, text=param_label)
            entry = tk.Entry(spectral_params_frame, width=20)
            label.grid(row=row, column=0, sticky="e", padx=5, pady=2)
            entry.grid(row=row, column=1, sticky="w", pady=2)

            spectral_entries[param_key] = (label, entry)
            value = saved_args.get(param_key, DEFAULT_ARGS.get(param_key, ""))
            entry.insert(0, value)

            if param_key in help_dict:
                CreateToolTip(entry, help_dict[param_key])
            row += 1


# Bind spectral model entry update event
model_entry.bind("<FocusOut>", lambda event: update_spectral_fields(saved_args))
model_entry.bind("<Return>", lambda event: update_spectral_fields(saved_args))


# --- Buttons ---
tk.Button(buttons_frame, text="Run Script", command=run_script).pack(
    side="left", padx=10
)
tk.Button(buttons_frame, text="Help", command=show_help).pack(side="left", padx=10)
tk.Button(buttons_frame, text="Reset", command=reset_form).pack(side="left", padx=10)
tk.Button(buttons_frame, text="Load Config", command=load_json_config).pack(
    side="left", padx=10
)
tk.Button(buttons_frame, text="Save Config", command=save_json_config).pack(
    side="left", padx=10
)
status_var = tk.StringVar(value="Ready...")
status_label = tk.Label(
    root, textvariable=status_var, fg="cyan", font=("Helvetica", 16, "bold")
)
status_label.pack(pady=5)


# --- Load last used arguments ---
if os.path.exists("last_used_args.json"):
    with open("last_used_args.json") as f:
        saved_args = json.load(f)
    for key, val in saved_args.items():
        if key in entries:
            entries[key].delete(0, tk.END)
            entries[key].insert(0, val)
        elif key == "LightCurve":
            lightcurve_var.set(val == True or val == "True")
        elif key == "IncludeNearby":
            include_nearby_var.set(val == True or val == "True")
        elif key == "Debug":
            debug_mode_var.set(val == True or val == "True")
        elif key == "SpectralModel":
            spectral_model_var.set(val)
        else:
            if key in spectral_entries:
                spectral_entries[key][1].delete(0, tk.END)
                spectral_entries[key][1].insert(0, val)
    update_spectral_fields(saved_args=saved_args)
else:
    saved_args = {}
    # Initialize spectral fields on startup
    update_spectral_fields(saved_args=saved_args)

menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Load Configuration", command=load_json_config)
file_menu.add_command(label="Save Configuration", command=save_json_config)
file_menu.add_separator()
menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

root.mainloop()
