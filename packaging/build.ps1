param([string]$Version = "0.2.0")

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    & "D:\PycharmProjects\python312\python.exe" -m PyInstaller --noconfirm --clean (Join-Path $PSScriptRoot "deepseek-pet.spec")
    $dist = Join-Path $root "dist\DeepSeekPet"
    foreach ($file in @("README.md", "README.en.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "DISCLAIMER.md", "SECURITY.md", "CONTRIBUTING.md")) {
        $path = Join-Path $root $file
        if (Test-Path $path) { Copy-Item $path -Destination $dist -Force }
    }
    $docs = Join-Path $root "docs"
    $destDocs = Join-Path $dist "docs"
    New-Item -ItemType Directory -Force -Path (Join-Path $destDocs "screenshots") | Out-Null
    foreach ($file in @("configuration.md", "privacy.md", "build.md")) {
        $path = Join-Path $docs $file
        if (Test-Path $path) { Copy-Item $path -Destination $destDocs -Force }
    }
    if (Test-Path (Join-Path $docs "screenshots")) {
        Copy-Item (Join-Path $docs "screenshots\*") -Destination (Join-Path $destDocs "screenshots") -Force
    }
    $zip = Join-Path $root "dist\DeepSeekPet-$Version-win-x64.zip"
    if (Test-Path $zip) { Remove-Item $zip -Force }
    Compress-Archive -Path (Join-Path $dist "*") -DestinationPath $zip
    Write-Host "Built: $zip"
} finally {
    Pop-Location
}
