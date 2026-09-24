@echo off
setlocal EnableExtensions
set "SBM_ROOT=%~dp0"
set "GIT_BASH_EXE="

for /f "delims=" %%G in ('where git.exe 2^>nul') do if not defined GIT_BASH_EXE call :from_git "%%~fG"
if not defined GIT_BASH_EXE for /f "delims=" %%B in ('where bash.exe 2^>nul') do if not defined GIT_BASH_EXE call :from_bash "%%~fB"
if not defined GIT_BASH_EXE call :standard "%ProgramFiles%\Git"
if not defined GIT_BASH_EXE call :standard "%ProgramW6432%\Git"
if not defined GIT_BASH_EXE call :standard "%ProgramFiles(x86)%\Git"

if not defined GIT_BASH_EXE (
  >&2 echo ERROR: Git Bash no esta disponible
  exit /b 1
)

"%GIT_BASH_EXE%" "%SBM_ROOT%sbm" %*
exit /b %ERRORLEVEL%

:from_git
for %%D in ("%~dp1..") do set "GIT_ROOT=%%~fD"
call :standard "%GIT_ROOT%"
exit /b 0

:from_bash
set "BASH_CANDIDATE=%~f1"
echo(%BASH_CANDIDATE%| findstr /i /c:"\Windows\System32\" /c:"\Windows\Sysnative\" >nul && exit /b 0
for %%D in ("%~dp1..") do set "GIT_ROOT=%%~fD"
if exist "%GIT_ROOT%\cmd\git.exe" set "GIT_BASH_EXE=%BASH_CANDIDATE%"
exit /b 0

:standard
if exist "%~1\bin\bash.exe" set "GIT_BASH_EXE=%~1\bin\bash.exe"
if not defined GIT_BASH_EXE if exist "%~1\usr\bin\bash.exe" set "GIT_BASH_EXE=%~1\usr\bin\bash.exe"
exit /b 0
