@echo off

rem Définir les variables pour les chemins et les arguments
set PYTHON_EXE_PATH=C:\Program Files\Python312\python.exe
set SCRIPT_PATH=C:\Program Files\PIPC\Interfaces\PI_UFL\_Scripts\SplitMESFiles.py
set INPUT_JSON_FOLDER=C:\Program Files\PIPC\Interfaces\PI_UFL\MES_UFL\Input
set OUTPUT_FOLDER=C:\Program Files\PIPC\Interfaces\PI_UFL\PI_UFL\Input
set BACKUP_FOLDER=C:\Program Files\PIPC\Interfaces\PI_UFL\MES_UFL\Done
set LOG_FOLDER=C:\Program Files\PIPC\Interfaces\PI_UFL\MES_UFL\Logs
set SUFFIXE=.PV

rem Appeler le script Python avec les paramètres
@echo on
"%PYTHON_EXE_PATH%" "%SCRIPT_PATH%" --input_json_folder "%INPUT_JSON_FOLDER%" --output_folder "%OUTPUT_FOLDER%" --backup_folder "%BACKUP_FOLDER%" --log_folder "%LOG_FOLDER%" --suffixe "%SUFFIXE%"
