@echo off
REM Activate the Anaconda environment
call env\Scripts\activate
REM Call the service script passed as an argument
call %1
