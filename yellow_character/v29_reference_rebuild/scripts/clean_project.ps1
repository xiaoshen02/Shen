$ErrorActionPreference = 'Stop'
$workspaceRoot = 'C:\Users\L\Desktop\git'
$projectRoot = Join-Path $workspaceRoot 'yellow_character'
$outputRoot = 'C:\Users\L\.codex\visualizations\2026\10\23\01a166ac-17cc-79c0-a443-2a4a3a7357fd'
$archiveOut = Join-Path $outputRoot 'yellow_character_history'
$manifestPath = Join-Path $projectRoot 'history\cleanup_manifest.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
if (-not $manifest.crc_verified) { throw 'Archive has not passed CRC verification.' }
$archiveSource = (Resolve-Path -LiteralPath $manifest.archive).ProviderPath
if (-not $archiveSource.StartsWith($projectRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected archive source.' }
if ((Get-FileHash -LiteralPath $archiveSource -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifest.archive_sha256) { throw 'Archive hash mismatch.' }
$archiveCreated = (Get-Item -LiteralPath $archiveSource).CreationTimeUtc

# Verify all targets before the first recursive deletion.
$resolvedTargets = @()
$protected = @($projectRoot, (Join-Path $projectRoot 'v29_reference_rebuild'), (Join-Path $projectRoot 'v28_hand_refined\YellowFriend_hand_refined.blend'))
foreach ($target in $manifest.targets) {
    $resolved = (Resolve-Path -LiteralPath $target).ProviderPath
    if (-not $resolved.StartsWith($projectRoot + '\', [StringComparison]::OrdinalIgnoreCase) -or $resolved -in $protected -or $resolved.StartsWith((Join-Path $projectRoot 'v29_reference_rebuild') + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Unsafe cleanup target: $resolved" }
    $reparse = Get-Item -LiteralPath $resolved -Force
    if ($reparse.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse point: $resolved" }
    if ($reparse.PSIsContainer) {
        if (Get-ChildItem -LiteralPath $resolved -Recurse -Force | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) { throw "Nested reparse point: $resolved" }
    }
    $resolvedTargets += $resolved
}
foreach ($entry in $manifest.entries) {
    $full = [IO.Path]::GetFullPath((Join-Path $projectRoot $entry.path))
    if (-not $full.StartsWith($projectRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe archive entry path.' }
    $item = Get-Item -LiteralPath $full -Force
    if ($item.Length -ne $entry.bytes -or $item.LastWriteTimeUtc -gt $archiveCreated) { throw "Source changed since archive: $full" }
}

# Keep the recoverable history outside git, in the task's allowed output root.
$resolvedOutput = [IO.Path]::GetFullPath($archiveOut)
if (-not $resolvedOutput.StartsWith($outputRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe archive destination.' }
New-Item -ItemType Directory -Path $archiveOut -Force | Out-Null
$archiveDestination = Join-Path $archiveOut (Split-Path -Leaf $archiveSource)
if (Test-Path -LiteralPath $archiveDestination) { throw 'Archive destination already exists.' }
Move-Item -LiteralPath $archiveSource -Destination $archiveDestination
if ((Get-FileHash -LiteralPath $archiveDestination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifest.archive_sha256) { throw 'Moved archive hash mismatch.' }
$manifest.archive = $archiveDestination
$manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath -Encoding utf8
Copy-Item -LiteralPath $manifestPath -Destination (Join-Path $archiveOut 'cleanup_manifest.json')

foreach ($resolved in $resolvedTargets) { Remove-Item -LiteralPath $resolved -Recurse -Force }

$debug = @('before_front.png','before_side.png','inspection.json','scripts\inspect_scene.py')
foreach ($name in $debug) {
    $path = [IO.Path]::GetFullPath((Join-Path $projectRoot ('v29_reference_rebuild\' + $name)))
    if (-not $path.StartsWith((Join-Path $projectRoot 'v29_reference_rebuild') + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe debug path.' }
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
}
$emptyRemoved = @()
Get-ChildItem -LiteralPath $workspaceRoot -Directory -Force | Where-Object { $_.Name.StartsWith('〱㥜㉥') -or $_.Name.StartsWith('改〲㑦') } | ForEach-Object {
    $resolved = (Resolve-Path -LiteralPath $_.FullName).ProviderPath
    if ((Split-Path -Parent $resolved) -ne $workspaceRoot) { throw 'Unexpected empty-directory parent.' }
    if (@(Get-ChildItem -LiteralPath $resolved -Force).Count -eq 0) { Remove-Item -LiteralPath $resolved -Force; $emptyRemoved += $resolved }
}
$report = [pscustomobject]@{ ArchivedFiles=$manifest.files; ArchivedSourceBytes=$manifest.source_bytes; Archive=$archiveDestination; ArchiveSHA256=$manifest.archive_sha256; RemovedEmptyDirectories=$emptyRemoved; RemovedDebugFiles=$debug; Baseline='v28_hand_refined\YellowFriend_hand_refined.blend'; Current='v29_reference_rebuild' }
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $projectRoot 'history\cleanup_result.json') -Encoding utf8
$report | ConvertTo-Json -Depth 6
