$ScriptPath = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$VenvPath = Join-Path $ScriptPath "venv"
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
$LogPath = Join-Path $ScriptPath "logs"

# --- PID Storage ---
$RasaServerJob = $null
$RasaActionsJob = $null
$HttpServerJob = $null

# --- Cleanup Function ---
function Stop-AllProcesses {
    Write-Host "`nCaught signal or script ending, cleaning up..."
    if ($HttpServerJob) {
        Write-Host "Stopping HTTP Server (Job ID $($HttpServerJob.Id))..."
        Stop-Job -Job $HttpServerJob -Force -ErrorAction SilentlyContinue
        Remove-Job -Job $HttpServerJob -Force -ErrorAction SilentlyContinue
    }
    if ($RasaActionsJob) {
        Write-Host "Stopping Rasa Actions Server (Job ID $($RasaActionsJob.Id))..."
        Stop-Job -Job $RasaActionsJob -Force -ErrorAction SilentlyContinue
        Remove-Job -Job $RasaActionsJob -Force -ErrorAction SilentlyContinue
    }
    if ($RasaServerJob) {
        Write-Host "Stopping Rasa Server (Job ID $($RasaServerJob.Id))..."
        Stop-Job -Job $RasaServerJob -Force -ErrorAction SilentlyContinue
        Remove-Job -Job $RasaServerJob -Force -ErrorAction SilentlyContinue
    }
    Write-Host "Cleanup attempt complete."
}

try {
    # Trap Ctrl+C (SIGINT)
    $null = [System.Console]::TreatControlCAsInput # Prevent Ctrl+C from immediately terminating the script
    Register-EngineEvent -SourceIdentifier ([System.Management.Automation.PsEngineEvent]::Exiting) -Action { Stop-AllProcesses } -Forward

    Write-Host "Activating Python virtual environment..."
    # ... (venv activation from previous script) ...
    if (-not (Test-Path $ActivateScript)) { Write-Error "Venv not found"; exit 1 }
    . $ActivateScript

    if (-not (Test-Path $LogPath)) { New-Item -ItemType Directory -Path $LogPath | Out-Null }

    $RasaDir = Join-Path $ScriptPath "rasa"
    $UIDir = Join-Path $ScriptPath "UI"
    $RasaExe = Join-Path $VenvPath "Scripts\rasa.exe"
    $PythonExe = Join-Path $VenvPath "Scripts\python.exe"

    Write-Host "Starting Rasa Server as a background job..."
    $RasaServerJob = Start-Job -Name "RasaServer" -ScriptBlock {
        param($RasaDirParam, $RasaExeParam, $LogPathParam)
        Set-Location -Path $RasaDirParam
        & $RasaExeParam run 2>&1 | Out-File -FilePath (Join-Path $LogPathParam "rasa_server.log") -Append
    } -ArgumentList $RasaDir, $RasaExe, $LogPath
    Write-Host "Rasa Server started as job ID $($RasaServerJob.Id)."
    Start-Sleep -Seconds 3

    Write-Host "Starting Rasa Actions Server as a background job..."
    $RasaActionsJob = Start-Job -Name "RasaActions" -ScriptBlock {
        param($RasaDirParam, $RasaExeParam, $LogPathParam)
        Set-Location -Path $RasaDirParam
        & $RasaExeParam run actions 2>&1 | Out-File -FilePath (Join-Path $LogPathParam "rasa_actions.log") -Append
    } -ArgumentList $RasaDir, $RasaExe, $LogPath
    Write-Host "Rasa Actions Server started as job ID $($RasaActionsJob.Id)."
    Start-Sleep -Seconds 3

    Write-Host "Starting Python HTTP Server for UI as a background job..."
    $HttpServerJob = Start-Job -Name "HttpServer" -ScriptBlock {
        param($PythonExeParam, $UIDirParam, $LogPathParam)
        & $PythonExeParam -m http.server 35109 --directory $UIDirParam 2>&1 | Out-File -FilePath (Join-Path $LogPathParam "http_server.log") -Append
    } -ArgumentList $PythonExe, $UIDir, $LogPath
    Write-Host "HTTP Server started as job ID $($HttpServerJob.Id)."
    Start-Sleep -Seconds 1

    Write-Host "Starting Main Python Assistant (core/main.py)... Press Ctrl+C to stop all."
    # This runs in the foreground
    & $PythonExe (Join-Path $ScriptPath "core\main.py")

}
finally {
    # This block executes when the script exits, whether normally or by Ctrl+C (due to the trap) or error
    Stop-AllProcesses
    Write-Host "Script finished."
    # You might still need to press Enter if the console is waiting for TreatControlCAsInput
}
