$env:Path = "C:\Program Files\nodejs;" + $env:Path
Write-Host "PATH is set to:" $env:Path
& "C:\Program Files\nodejs\npm.cmd" install
