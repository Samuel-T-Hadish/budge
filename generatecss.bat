@echo off
echo Generating Tailwind CSS...

:: Assuming tailwindcss.exe is now in the bin directory at the project root
tailwindcss.exe -i .\budge\tailwind\styles.css -o .\budge\assets\tailwind.css --minify 

echo Tailwind CSS generated successfully.
pause
