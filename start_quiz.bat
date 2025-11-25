@echo off
echo Installing required packages...
call ..\..\.venv\Scripts\pip.exe install flask flask-cors

echo.
echo Starting Quiz Web Server...
echo.
echo Open your browser and go to: http://localhost:5000
echo.
start http://localhost:5000/quiz_web.html
call ..\..\.venv\Scripts\python.exe app.py
