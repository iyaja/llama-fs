# Set the folder to the directory where the script is running from
$FOLDER_HOME = $PSScriptRoot
$VENV_EXIST = 0
Write-Host "Folder set to $FOLDER_HOME"

# Recursively iterate through all folders in the project to find the venv
Get-ChildItem -Path $FOLDER_HOME -Recurse -Directory | ForEach-Object {
    $folder = $_.FullName
    if (Test-Path "$folder\Activate.ps1") {
        Write-Host "Python venv found in $folder"
        Set-Location $folder
        # Check if running in PowerShell
        if ($Host.Name -eq "ConsoleHost" -or $Host.Name -eq "Visual Studio Code Host") {
            # Write-Host "Running PowerShell script"
            .\Activate.ps1
            Set-Location $FOLDER_HOME
            $VENV_EXIST = 1
        } else {
            Write-Host "Running batch file from CMD (not supported)"
            # You can't run a batch file from PowerShell, so this branch is not needed
        }
        break
    }
}

if ($VENV_EXIST -eq 0) {
    # If no venv found, create a new one and install requirements
    Write-Host "No Python venv found. Creating a new one..."
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    Write-Host "Installing Python requirements..."
    pip install -r requirements.txt
    Write-Host "Python venv created and requirements installed."
}
