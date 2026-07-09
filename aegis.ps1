#!/usr/bin/env pwsh


$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$venvDir = Join-Path $repoRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
$venvAegis = Join-Path $venvDir "Scripts\aegis.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Premiere utilisation : creation de l'environnement (ca prend une minute)..." -ForegroundColor Cyan

    python -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Impossible de creer le venv. Verifie que Python 3.12+ est installe et dans le PATH."
        exit 1
    }

    & $venvPython -m pip install --quiet --upgrade pip
    & $venvPython -m pip install --quiet -e "$repoRoot\backend[dev,api]" -e "$repoRoot\cli[dev]"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "L'installation des dependances a echoue."
        exit 1
    }

    Write-Host "Environnement pret." -ForegroundColor Green
}

& $venvAegis @args
exit $LASTEXITCODE
