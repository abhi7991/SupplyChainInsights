import os
import subprocess

def make_env(name,cuda_version):
    try:
        with open("CreateCondaEnv.bat", 'w') as bat_file:
            bat_file.write(f'''@echo off
setlocal enabledelayedexpansion

cd /D "%~dp0"

set PATH=%PATH%;%SystemRoot%\system32

echo "%CD%"| findstr /C:" " >nul && echo This script relies on Miniconda which can not be silently installed under a path with spaces. && goto end

u/rem Check for special characters in installation path
set "SPCHARMESSAGE="WARNING: Special characters were detected in the installation path!" "         This can cause the installation to fail!""
echo "%CD%"| findstr /R /C:"[!#\$%&()\*+,;<=>?@\[\]\^`{{|}}~]" >nul && (
    call :PrintBigMessage %SPCHARMESSAGE%
)
set SPCHARMESSAGE=

u/rem fix failed install when installing to a separate drive
set TMP=%cd%\{name}
set TEMP=%cd%\{name}

@rem deactivate existing conda envs as needed to avoid conflicts
(call conda deactivate && call conda deactivate && call conda deactivate) 2>nul

@rem config
set INSTALL_DIR=%cd%\{name}
set CONDA_ROOT_PREFIX=%cd%\{name}\conda
set INSTALL_ENV_DIR=%cd%\{name}\env
set MINICONDA_DOWNLOAD_URL=https://repo.anaconda.com/miniconda/Miniconda3-py310_23.3.1-0-Windows-x86_64.exe
set MINICONDA_CHECKSUM=307194e1f12bbeb52b083634e89cc67db4f7980bd542254b43d3309eaf7cb358
set conda_exists=F

@rem figure out whether git and conda needs to be installed
call "%CONDA_ROOT_PREFIX%\_conda.exe" --version >nul 2>&1
if "%ERRORLEVEL%" EQU "0" set conda_exists=T

@rem (if necessary) install git and conda into a contained environment
@rem download conda
if "%conda_exists%" == "F" (
    echo Downloading Miniconda from %MINICONDA_DOWNLOAD_URL% to %INSTALL_DIR%\miniconda_installer.exe

    mkdir "%INSTALL_DIR%"
    call curl -Lk "%MINICONDA_DOWNLOAD_URL%" > "%INSTALL_DIR%\miniconda_installer.exe" || ( echo. && echo Miniconda failed to download. && goto end )

    for /f %%a in ('CertUtil -hashfile "%INSTALL_DIR%\miniconda_installer.exe" SHA256 ^| find /i /v " " ^| find /i "%MINICONDA_CHECKSUM%"') do (
        set "output=%%a"
    )

    if not defined output (
        echo The checksum verification for miniconda_installer.exe has failed.
        del "%INSTALL_DIR%\miniconda_installer.exe"
        goto end
    ) else (
        echo The checksum verification for miniconda_installer.exe has passed successfully.
    )

    echo Installing Miniconda to %CONDA_ROOT_PREFIX%
    start /wait "" "%INSTALL_DIR%\miniconda_installer.exe" /InstallationType=JustMe /NoShortcuts=1 /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=%CONDA_ROOT_PREFIX%

    @rem test the conda binary
    echo Miniconda version:
    call "%CONDA_ROOT_PREFIX%\_conda.exe" --version || ( echo. && echo Miniconda not found. && goto end )

    @rem delete the Miniconda installer
    del "%INSTALL_DIR%\miniconda_installer.exe"
)

@rem create the installer env
if not exist "%INSTALL_ENV_DIR%" (
    echo Packages to install: %PACKAGES_TO_INSTALL%
    call "%CONDA_ROOT_PREFIX%\_conda.exe" create --no-shortcuts -y -k --prefix "%INSTALL_ENV_DIR%" python=3.11 || ( echo. && echo Conda environment creation failed. && goto end )
)

@rem check if conda environment was actually created
if not exist "%INSTALL_ENV_DIR%\python.exe" ( echo. && echo Conda environment is empty. && goto end )

@rem environment isolation
set PYTHONNOUSERSITE=1
set PYTHONPATH=
set PYTHONHOME=
set "CUDA_PATH=%INSTALL_ENV_DIR%"
set "CUDA_HOME=%CUDA_PATH%"

@rem activate installer env
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( echo. && echo Miniconda hook not found. && goto end )



@rem below are functions for the script   next line skips these during normal execution
goto end

:PrintBigMessage
echo. && echo.
echo *******************************************************************
for %%M in (%*) do echo * %%~M
echo *******************************************************************
echo. && echo.
exit /b

:end
''')
            bat_file.close()

        with open("InstallUnslothPakages.bat", 'w') as bat_file2:
            bat_file2.write(f'''@echo off

cd /D "%~dp0"

set PATH=%PATH%;%SystemRoot%\system32

echo "%CD%"| findstr /C:" " >nul && echo This script relies on Miniconda which can not be silently installed under a path with spaces. && goto end

@rem fix failed install when installing to a separate drive
set TMP=%cd%\{name}
set TEMP=%cd%\{name}

@rem deactivate existing conda envs as needed to avoid conflicts
(call conda deactivate && call conda deactivate && call conda deactivate) 2>nul

@rem config
set CONDA_ROOT_PREFIX=%cd%\{name}\conda
set INSTALL_ENV_DIR=%cd%\{name}\env

@rem environment isolation
set PYTHONNOUSERSITE=1
set PYTHONPATH=
set PYTHONHOME=
set "CUDA_PATH=%INSTALL_ENV_DIR%"
set "CUDA_HOME=%CUDA_PATH%"

@rem activate installer env
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( echo. && echo Miniconda hook not found. && goto end )

@rem enter commands
cmd /k "conda create --name {name} python=3.11 -y && conda activate {name} && pip install torch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0 --index-url https://download.pytorch.org/whl/{cuda_version} && pip install bitsandbytes==0.43.1 && pip install transformers==4.42.3 && pip install datasets==2.20.0 && pip install accelerate==0.30.1 && pip install peft==0.11.1 && pip install trl==0.8.6 && git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git && cd LLaMA-Factory && pip install -e ".[gptq,awq,metrics]" && cd.. && pip install "unsloth[{cuda_version}-torch230] @ git+https://github.com/JayAnderson360/unsloth_Windows.git" && pip install -U numpy==1.26.4 && pip install https://huggingface.co/LightningJay/triton-2.1.0-python3.11-win_amd64-wheel/resolve/main/triton-2.1.0-cp311-cp311-win_amd64.whl?download=true && conda install -y -c conda-forge/label/llvm_rc clangdev && exit"

exit /b
:end
''')
            bat_file2.close()
        print(f"Creating the environment: {name}")
        os.system(r'start /wait CreateCondaEnv.bat ^&^& exit')
        os.system(r'start /wait InstallUnslothPakages.bat ^&^& exit')
        subprocess.run(r'del CreateCondaEnv.bat', shell=True, check=True)
        subprocess.run(r'del InstallUnslothPakages.bat', shell=True, check=True)
        print(f"{name} has been Created :)")
    except subprocess.CalledProcessError as e:
        print(f"Error creating the environment: {e.output}")



def write_bat_file(bat_filename, env_name):
    with open(bat_filename, 'w') as bat_file:
        bat_file.write(f'''@echo off

cd /D "%~dp0"

set PATH=%PATH%;%SystemRoot%\system32

echo "%CD%"| findstr /C:" " >nul && echo This script relies on Miniconda which can not be silently installed under a path with spaces. && goto end

@rem fix failed install when installing to a separate drive
set TMP=%cd%\{env_name}
set TEMP=%cd%\{env_name}

@rem deactivate existing conda envs as needed to avoid conflicts
(call conda deactivate && call conda deactivate && call conda deactivate) 2>nul

@rem config
set CONDA_ROOT_PREFIX=%cd%\{env_name}\conda
set INSTALL_ENV_DIR=%cd%\{env_name}\env

@rem environment isolation
set PYTHONNOUSERSITE=1
set PYTHONPATH=
set PYTHONHOME=
set "CUDA_PATH=%INSTALL_ENV_DIR%"
set "CUDA_HOME=%CUDA_PATH%"

@rem activate installer env
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( echo. && echo Miniconda hook not found. && goto end )

call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate {env_name} 
for /f "tokens=*" %%i in ('where clang.exe') do set CC=%%i 
echo CC Path is set to: %CC% 

@rem enter commands
cmd /k "%*"

:end
''')
        bat_file.close()

def main():
    env_name = input("Enter the name of the environment you want to create: ")
    env_name="{}".format(env_name).replace(" ","_")
    env_name="{}".format(env_name).replace("\\","_")
    env_name="{}".format(env_name).replace("!","_")
    env_name="{}".format(env_name).replace("#","_")
    env_name="{}".format(env_name).replace("$","_")
    env_name="{}".format(env_name).replace("%","_")
    env_name="{}".format(env_name).replace("&","_")
    env_name="{}".format(env_name).replace("(","_")
    env_name="{}".format(env_name).replace(")","_")
    env_name="{}".format(env_name).replace("*","_")
    env_name="{}".format(env_name).replace("+","_")
    env_name="{}".format(env_name).replace(",","_")
    env_name="{}".format(env_name).replace(";","_")
    env_name="{}".format(env_name).replace("!","_")
    env_name="{}".format(env_name).replace("<","_")
    env_name="{}".format(env_name).replace("=","_")
    env_name="{}".format(env_name).replace(">","_")
    env_name="{}".format(env_name).replace("?","_")
    env_name="{}".format(env_name).replace("@","_")
    env_name="{}".format(env_name).replace("[","_")
    env_name="{}".format(env_name).replace("]","_")
    env_name="{}".format(env_name).replace("^","_")
    env_name="{}".format(env_name).replace("`","_")
    env_name="{}".format(env_name).replace("{","_")
    env_name="{}".format(env_name).replace("}","_")
    cuda_version = ""
    while True:
        print("CUDA Versions:\n1. CUDA 11.8\n2. CUDA 12.1\n")
        x=str(input("Pls select a CUDA version by typing the number 1 or 2: "))
        if x=="1":
            cuda_version = "cu118" 
            break
        elif x=="2":
            cuda_version = "cu121" 
            break
        else:
            print("Warning!!! Invalid Selection. Try Again!")
    make_env(env_name,cuda_version)
    bat_filename = ("Activate_enviroment_%s.bat" % env_name)
    write_bat_file(bat_filename,env_name)

main()