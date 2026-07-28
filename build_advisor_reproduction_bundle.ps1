param(
    [string]$BundleName = "advisor_reproduction_bundle_zh_2026-07-24"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BundleRoot = Join-Path $ProjectRoot $BundleName

if (Test-Path -LiteralPath $BundleRoot) {
    $existing = Get-ChildItem -LiteralPath $BundleRoot -Force
    if ($existing.Count -gt 0) {
        throw "Bundle directory already exists and is not empty: $BundleRoot"
    }
} else {
    New-Item -ItemType Directory -Path $BundleRoot | Out-Null
}

# All executable research and validation code lives at the bundle root so that
# the original relative paths (data/, results/, outputs/) remain reproducible.
Get-ChildItem -LiteralPath $ProjectRoot -File -Filter "*.py" |
    Copy-Item -Destination $BundleRoot

Copy-Item -LiteralPath (Join-Path $ProjectRoot "README.md") -Destination (Join-Path $BundleRoot "PROJECT_README.md")

# Copy the complete live proof/evidence tree, but only text, tables, JSON and PNG.
$sourceOutputs = Join-Path $ProjectRoot "outputs\researchwrite\hypergraph-stopping-time"
$targetOutputs = Join-Path $BundleRoot "outputs\researchwrite\hypergraph-stopping-time"
Get-ChildItem -LiteralPath $sourceOutputs -Recurse -File | Where-Object {
    $_.Extension.ToLowerInvariant() -in @(".md", ".json", ".bib", ".csv", ".png")
} | ForEach-Object {
    $relative = $_.FullName.Substring($sourceOutputs.Length).TrimStart('\')
    $target = Join-Path $targetOutputs $relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
    Copy-Item -LiteralPath $_.FullName -Destination $target
}

# Only the source inputs actually used by the formal topology runs are copied.
$dataFiles = @(
    "data\raw\ln-geolocated-2019-2023\README.md",
    "data\raw\ln-geolocated-2019-2023\selected_snapshots\20201014.gml.geo",
    "data\raw\ln-geolocated-2019-2023\selected_snapshots\20220531.gml.geo",
    "data\raw\ln-geolocated-2019-2023\selected_snapshots\20230716.gml.geo",
    "data\raw\mempool-lightning-2026-07-22\README.md",
    "data\raw\mempool-lightning-2026-07-22\channels-geo.json",
    "data\raw\mempool-lightning-2026-07-22\statistics-latest.json"
)
foreach ($relative in $dataFiles) {
    $source = Join-Path $ProjectRoot $relative
    $target = Join-Path $BundleRoot $relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $target
}

# Preserve all compact formula tables at results/ root.
$sourceResults = Join-Path $ProjectRoot "results"
$targetResults = Join-Path $BundleRoot "results"
New-Item -ItemType Directory -Path $targetResults -Force | Out-Null
Get-ChildItem -LiteralPath $sourceResults -File | Copy-Item -Destination $targetResults

# Authoritative result families. Quick, draft and rejected runs are intentionally
# omitted; formal, replication, exact-anchor, sensitivity and comparison evidence remain.
$resultDirectories = @(
    "discrete-gaussian-bridge",
    "network",
    "t12-positive-competition",
    "t12-positive-competition-exact-anchors",
    "t12-positive-competition-replication",
    "t12-positive-competition-replication-comparison",
    "t18-cross-topology",
    "t18-cross-topology-replication",
    "t18-exact-anchors",
    "t18-weakest-sensitivity",
    "lightning-real-topology-mapping",
    "lightning-real-topology-preflight",
    "lightning-real-topology-formal",
    "lightning-real-topology-replication",
    "lightning-real-topology-replication-comparison",
    "lightning-real-topology-pooled-sensitivity",
    "lightning-current-2026-preflight",
    "lightning-current-2026-formal",
    "lightning-current-2026-replication",
    "lightning-current-2026-replication-comparison",
    "lightning-current-2026-pooled-sensitivity",
    "lightning-structural-sign-analysis",
    "lightning-drift-interpolation-preflight",
    "lightning-drift-interpolation-formal",
    "lightning-drift-interpolation-replication",
    "lightning-drift-interpolation-comparison",
    "lightning-sign-mechanism-closure",
    "stopping-event-mapping-validation"
)
foreach ($name in $resultDirectories) {
    $source = Join-Path $sourceResults $name
    $target = Join-Path $targetResults $name
    Copy-Item -LiteralPath $source -Destination $target -Recurse
}

Write-Output $BundleRoot
