<img src="ChatGPTGammaPyScriptLogo.png" alt="Project Logo" width="500">


This Toolkit is used to run gammapy using VERITAS data.

- It can be run by using either
    - DL3toDL5.py on the command line,
    -  the GUI: "RunGammaPyGUI.py". 

- To run the GUI by clicking on it you need to setup a bash script wherever you want to run the GUI e.g. your Desktop
- The script should include:
    -  #!/bin/bash
    -  Activate the environment where you have the [required packages](EnvironmentPackages.txt) (source ~/gpy_toolkit/bin/activate)
    -  Change directory to wherever RunGammapyGUI.py is (cd /your/path/to/GammapyToolkit/)
    -  Run the script (python RunGammaPyGUI.py)
- If you wish, you can also give your bash script a logo such as the one provided [here](ChatGPTGammaPyScriptLogo.png).
    - On a mac, right click on the file, click `Get Info`, then click on the icon on the top left corner and paste your image there. 
