# start-hunter.ps1 - launcher for hunter daemon (started hidden via run-hunter.vbs)
$env:PYTHONIOENCODING = 'utf-8'
Set-Location $PSScriptRoot
py -3 (Join-Path $PSScriptRoot 'bot.py')
