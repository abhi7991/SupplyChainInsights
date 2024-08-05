@echo off

cd /D "%~dp0"

set PATH=%PATH%;%SystemRoot%\system32

echo "%CD%"| findstr /C:" " >nul && echo This script relies on Miniconda which can not be silently installed under a path with spaces. && goto end

@rem fix failed install when installing to a separate drive
set TMP=%cd%\unsloth_env
set TEMP=%cd%\unsloth_env

@rem deactivate existing conda envs as needed to avoid conflicts
(call conda deactivate && call conda deactivate && call conda deactivate) 2>nul

@rem config
set CONDA_ROOT_PREFIX=%cd%\unsloth_env\conda
set INSTALL_ENV_DIR=%cd%\unsloth_env\env

@rem environment isolation
set PYTHONNOUSERSITE=1
set PYTHONPATH=
set PYTHONHOME=
set "CUDA_PATH=%INSTALL_ENV_DIR%"
set "CUDA_HOME=%CUDA_PATH%"

@rem activate installer env
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( echo. && echo Miniconda hook not found. && goto end )

call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate unsloth_env 
for /f "tokens=*" %%i in ('where clang.exe') do set CC=%%i 
echo CC Path is set to: %CC% 

@rem enter commands
cmd /k "%*"

:end
