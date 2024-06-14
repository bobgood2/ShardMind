echo Waiting for indexserve to be available: localhost:5001 
:check_service
curl http://localhost:5001 -s -o NUL
if errorlevel 1 (
    timeout /t 5 > NUL
    goto check_service
)

echo Waiting for plan_service to be available: localhost:8765 
:check_service2
curl http://localhost:8765 -s -o NUL
if errorlevel 1 (
    timeout /t 5 > NUL
    goto check_service2
)

echo localhost:5001 and localhost:8765 are available, starting app.


chainlit run App\chatbot.py