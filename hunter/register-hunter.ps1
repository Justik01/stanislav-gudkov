# register-hunter.ps1 - registers hunter autostart (run once)
# Primary: scheduled task AI-Hunter on logon.
# Fallback: copy run-hunter.vbs to Startup folder (task may need admin).
$vbs = Join-Path $PSScriptRoot 'run-hunter.vbs'
$ok = $false
$tr = 'wscript.exe "{0}"' -f $vbs
schtasks /Create /F /TN 'AI-Hunter' /SC ONLOGON /TR $tr 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { $ok = $true; Write-Host "Task AI-Hunter: created" }
if (-not $ok) {
  $startup = [Environment]::GetFolderPath('Startup')
  Copy-Item $vbs (Join-Path $startup 'run-hunter.vbs') -Force
  Write-Host "Task failed (admin?) - VBS copied to Startup: $startup"
}
Write-Host "--- Proverka ---"
schtasks /Query /TN 'AI-Hunter' /FO LIST 2>&1
