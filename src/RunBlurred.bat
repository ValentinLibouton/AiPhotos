@echo off
echo Veuillez entrer le chemin complet du dossier a analyser:
set /p dir_path="Chemin: "
python "C:\Users\destr\OneDrive\Documents\AiPhotos\blurred.py" "%dir_path%"
pause