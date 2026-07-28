$ErrorActionPreference = "Stop"
$BundleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $BundleRoot
python .\run_reproduction.py --mode quick
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
