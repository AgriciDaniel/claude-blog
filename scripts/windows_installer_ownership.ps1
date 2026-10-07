# Shared ownership engine for the Windows installer and uninstaller.
# Windows PowerShell 5.1 compatible. Dot-source this file, then call the
# exported Invoke-ClaudeBlogInstall or Invoke-ClaudeBlogUninstall function.

$script:CBReceiptOwner = "claude-blog-windows-installer"
$script:CBLegacyOwner = "claude-blog-reviewed-legacy-payload"
$script:CBHex64 = '^[0-9a-f]{64}$'

function Get-CBFullPath($Path) {
    return [System.IO.Path]::GetFullPath([string]$Path).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
}

function Test-CBPathUnderRoot($Path, $Root) {
    $fullPath = Get-CBFullPath $Path
    $fullRoot = Get-CBFullPath $Root
    if ($fullPath.Equals($fullRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $true
    }
    $prefix = $fullRoot + [System.IO.Path]::DirectorySeparatorChar
    return $fullPath.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)
}

function Assert-CBRelativePath($RelativePath) {
    $value = [string]$RelativePath
    if (-not $value -or $value.Contains('\') -or $value.StartsWith('/') -or
        $value.EndsWith('/') -or $value.Contains(':')) {
        throw "unsafe relative installation path: $value"
    }
    $parts = @($value.Split('/'))
    if ($parts.Count -lt 2 -or @($parts | Where-Object { -not $_ -or $_ -eq '.' -or $_ -eq '..' }).Count -gt 0) {
        throw "unsafe relative installation path: $value"
    }
    $allowed = $false
    if ($parts[0] -eq 'skills' -and $parts.Count -ge 3) {
        $allowed = ($parts[1] -eq 'blog' -or $parts[1] -match '^blog-[a-z0-9]+(?:-[a-z0-9]+)*$')
    } elseif ($parts[0] -eq 'agents' -and $parts.Count -eq 2) {
        $allowed = $parts[1] -match '^blog-[a-z0-9-]+\.md$'
    } elseif ($parts[0] -eq 'scripts' -and $parts.Count -eq 2) {
        $allowed = ($parts[1] -match '^[A-Za-z0-9_]+\.py$' -or $parts[1] -eq 'windows_installer_ownership.ps1')
    }
    if (-not $allowed) {
        throw "unsafe relative installation path: $value"
    }
    return $value
}

function Get-CBTargetPath($ProfileRoot, $RelativePath) {
    $relative = Assert-CBRelativePath $RelativePath
    $target = Join-Path (Get-CBFullPath $ProfileRoot) ($relative.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
    if (-not (Test-CBPathUnderRoot $target $ProfileRoot)) {
        throw "installation path escapes the Claude profile: $relative"
    }
    return Get-CBFullPath $target
}

function Test-CBReparsePoint($Item) {
    return (($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
}

function Assert-CBNoReparseAbsolutePath($Path) {
    $full = Get-CBFullPath $Path
    $root = [System.IO.Path]::GetPathRoot($full)
    $current = $root
    $remainder = $full.Substring($root.Length)
    foreach ($part in @($remainder.Split([System.IO.Path]::DirectorySeparatorChar) | Where-Object { $_ })) {
        $current = Join-Path $current $part
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if (Test-CBReparsePoint $item) {
                throw "unsafe reparse point in managed path: $current"
            }
        } else {
            break
        }
    }
}

function Assert-CBProfilePath($ProfileRoot, $Path) {
    if (-not (Test-CBPathUnderRoot $Path $ProfileRoot)) {
        throw "path escapes the Claude profile: $Path"
    }
    Assert-CBNoReparseAbsolutePath $ProfileRoot
    Assert-CBNoReparseAbsolutePath $Path
}

function Get-CBSha256($Path) {
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (Test-CBReparsePoint $item) { throw "refusing reparse-point file: $Path" }
    if (-not $item.PSIsContainer) {
        $stream = [System.IO.File]::Open($item.FullName, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $sha = [System.Security.Cryptography.SHA256]::Create()
        try {
            return ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
        } finally {
            $sha.Dispose()
            $stream.Dispose()
        }
    }
    throw "managed path is not a regular file: $Path"
}

function Get-CBTreeFiles($Root) {
    if (-not (Test-Path -LiteralPath $Root)) { return @() }
    $rootItem = Get-Item -LiteralPath $Root -Force
    if (Test-CBReparsePoint $rootItem) { throw "source payload directory is a reparse point: $Root" }
    if (-not $rootItem.PSIsContainer) { throw "source payload directory is not a directory: $Root" }
    $result = @()
    foreach ($item in @(Get-ChildItem -LiteralPath $Root -Force)) {
        if (Test-CBReparsePoint $item) { throw "source payload contains a reparse point: $($item.FullName)" }
        if ($item.PSIsContainer) {
            if ($item.Name -ne '__pycache__') { $result += @(Get-CBTreeFiles $item.FullName) }
        } elseif ($item.Name -notlike '*.pyc') {
            $result += $item
        }
    }
    return $result
}

function Add-CBPlanFile($Plan, $SourcePath, $RelativePath) {
    $relative = Assert-CBRelativePath $RelativePath
    if ($Plan.ContainsKey($relative)) { throw "duplicate installation destination: $relative" }
    $item = Get-Item -LiteralPath $SourcePath -Force -ErrorAction Stop
    if ($item.PSIsContainer -or (Test-CBReparsePoint $item)) { throw "source payload is not a regular file: $SourcePath" }
    $Plan[$relative] = [PSCustomObject]@{
        Path = $relative
        Source = $item.FullName
        Sha256 = Get-CBSha256 $item.FullName
    }
}

function Add-CBPlanTree($Plan, $SourceRoot, $TargetPrefix) {
    if (-not (Test-Path -LiteralPath $SourceRoot)) { return }
    $sourceFull = Get-CBFullPath $SourceRoot
    foreach ($file in @(Get-CBTreeFiles $sourceFull)) {
        $suffix = $file.FullName.Substring($sourceFull.Length).TrimStart('\', '/')
        Add-CBPlanFile $Plan $file.FullName (($TargetPrefix.TrimEnd('/') + '/' + $suffix.Replace('\', '/')))
    }
}

function Get-CBSourcePlan($SourceRoot) {
    $root = Get-CBFullPath $SourceRoot
    Assert-CBNoReparseAbsolutePath $root
    $plan = @{}
    $skills = @()
    $agents = @()
    $scripts = @()

    Add-CBPlanFile $plan (Join-Path $root 'skills/blog/SKILL.md') 'skills/blog/SKILL.md'
    Add-CBPlanTree $plan (Join-Path $root 'skills/blog/references') 'skills/blog/references'
    Add-CBPlanTree $plan (Join-Path $root 'skills/blog/templates') 'skills/blog/templates'
    $ledger = Join-Path $root 'data/google-updates.json'
    if (Test-Path -LiteralPath $ledger -PathType Leaf) {
        Add-CBPlanFile $plan $ledger 'skills/blog/data/google-updates.json'
    }

    foreach ($skill in @(Get-ChildItem -LiteralPath (Join-Path $root 'skills') -Directory -Force | Sort-Object Name)) {
        if ($skill.Name -eq 'blog') { continue }
        if (Test-CBReparsePoint $skill) { throw "source skill directory is a reparse point: $($skill.FullName)" }
        if ($skill.Name -notmatch '^blog-[a-z0-9]+(?:-[a-z0-9]+)*$') { continue }
        $skillMd = Join-Path $skill.FullName 'SKILL.md'
        if (-not (Test-Path -LiteralPath $skillMd -PathType Leaf)) { continue }
        $skills += $skill.Name
        Add-CBPlanFile $plan $skillMd "skills/$($skill.Name)/SKILL.md"
        foreach ($name in @('references', 'scripts', 'assets', 'templates')) {
            Add-CBPlanTree $plan (Join-Path $skill.FullName $name) "skills/$($skill.Name)/$name"
        }
    }

    foreach ($agent in @(Get-ChildItem -LiteralPath (Join-Path $root 'agents') -File -Filter 'blog-*.md' -Force | Sort-Object Name)) {
        $agents += $agent.Name
        Add-CBPlanFile $plan $agent.FullName "agents/$($agent.Name)"
    }
    foreach ($scriptFile in @(Get-ChildItem -LiteralPath (Join-Path $root 'scripts') -File -Filter '*.py' -Force | Sort-Object Name)) {
        $scripts += $scriptFile.Name
        Add-CBPlanFile $plan $scriptFile.FullName "scripts/$($scriptFile.Name)"
        if ($scriptFile.Name -eq 'analyze_blog.py') {
            Add-CBPlanFile $plan $scriptFile.FullName 'skills/blog/scripts/analyze_blog.py'
        }
    }
    $windowsHelper = Join-Path $root 'scripts/windows_installer_ownership.ps1'
    Add-CBPlanFile $plan $windowsHelper 'scripts/windows_installer_ownership.ps1'

    return [PSCustomObject]@{
        Files = $plan
        SkillNames = @($skills)
        AgentNames = @($agents)
        ScriptNames = @($scripts)
    }
}

function Read-CBLegacyInventory($Path) {
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($item.PSIsContainer -or (Test-CBReparsePoint $item)) { throw "reviewed legacy ownership inventory is unavailable: $Path" }
    try { $data = [System.IO.File]::ReadAllText($item.FullName) | ConvertFrom-Json -ErrorAction Stop }
    catch { throw "reviewed legacy ownership inventory is invalid: $Path" }
    if ($data.schema_version -ne 1 -or $data.owner -ne $script:CBLegacyOwner -or -not $data.files -or -not $data.revisions) {
        throw "reviewed legacy ownership inventory has an unsupported schema: $Path"
    }
    $revisionSet = @{}
    foreach ($revision in @($data.revisions)) {
        if (-not $revision.commit -or $revisionSet.ContainsKey([string]$revision.commit)) { throw "invalid legacy revision inventory" }
        $revisionSet[[string]$revision.commit] = $true
    }
    $records = @{}
    foreach ($property in @($data.files.PSObject.Properties)) {
        $relative = Assert-CBRelativePath $property.Name
        if ($records.ContainsKey($relative)) { throw "duplicate legacy inventory path: $relative" }
        $pathRecords = @()
        foreach ($record in @($property.Value)) {
            $hash = ([string]$record.sha256).ToLowerInvariant()
            $revision = [string]$record.revision
            if ($hash -notmatch $script:CBHex64 -or -not $revisionSet.ContainsKey($revision)) {
                throw "invalid legacy inventory record: $relative"
            }
            $pathRecords += [PSCustomObject]@{ Sha256 = $hash; Revision = $revision }
        }
        if ($pathRecords.Count -eq 0) { throw "empty legacy inventory record: $relative" }
        $records[$relative] = $pathRecords
    }
    return [PSCustomObject]@{ Records = $records; Revisions = @($revisionSet.Keys) }
}

function ConvertTo-CBReceipt($Plan, $Version) {
    $records = @()
    foreach ($relative in @($Plan.Keys | Sort-Object)) {
        $records += [ordered]@{ path = $relative; sha256 = $Plan[$relative].Sha256 }
    }
    $receipt = [ordered]@{
        schema_version = 2
        owner = $script:CBReceiptOwner
        version = [string]$Version
        files = $records
    }
    return (($receipt | ConvertTo-Json -Depth 5) + [Environment]::NewLine)
}

function Read-CBReceipt($ManifestPath, $ProfileRoot) {
    Assert-CBProfilePath $ProfileRoot $ManifestPath
    $item = Get-Item -LiteralPath $ManifestPath -Force -ErrorAction Stop
    if ($item.PSIsContainer -or (Test-CBReparsePoint $item)) { throw "installation receipt is not a regular file: $ManifestPath" }
    $raw = [System.IO.File]::ReadAllText($item.FullName)
    try { $data = $raw | ConvertFrom-Json -ErrorAction Stop }
    catch { return [PSCustomObject]@{ Kind = 'legacy'; Raw = $raw; Files = $null } }
    if ($data.schema_version -ne 2 -or $data.owner -ne $script:CBReceiptOwner -or $null -eq $data.files) {
        throw "unrecognized installation receipt: $ManifestPath"
    }
    $files = @{}
    foreach ($record in @($data.files)) {
        $relative = Assert-CBRelativePath ([string]$record.path)
        $hash = ([string]$record.sha256).ToLowerInvariant()
        if ($hash -notmatch $script:CBHex64) { throw "invalid receipt hash: $relative" }
        if ($files.ContainsKey($relative)) { throw "duplicate installation receipt path: $relative" }
        $files[$relative] = $hash
    }
    if ($files.Count -eq 0) { throw "installation receipt contains no files: $ManifestPath" }
    return [PSCustomObject]@{ Kind = 'v2'; Raw = $raw; Files = $files }
}

function Get-CBLegacyScopes($Raw, $ProfileRoot, $Inventory) {
    $scopes = @()
    foreach ($line in @($Raw -split "`r?`n")) {
        $value = $line.Trim()
        if (-not $value) { continue }
        if (-not [System.IO.Path]::IsPathRooted($value)) { throw "legacy manifest contains an unsafe path: $value" }
        $full = Get-CBFullPath $value
        if (-not (Test-CBPathUnderRoot $full $ProfileRoot)) { throw "legacy manifest contains an unsafe path: $value" }
        Assert-CBProfilePath $ProfileRoot $full
        $root = Get-CBFullPath $ProfileRoot
        $relative = $full.Substring($root.Length).TrimStart('\', '/').Replace('\', '/')
        $valid = $false
        if ($Inventory.Records.ContainsKey($relative)) { $valid = $true }
        elseif ($relative -match '^skills/(blog|blog-[a-z0-9]+(?:-[a-z0-9]+)*)$') {
            $prefix = $relative + '/'
            $valid = @($Inventory.Records.Keys | Where-Object { $_.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase) }).Count -gt 0
        }
        if (-not $valid) { throw "legacy manifest contains an unreviewed scope: $value" }
        $scopes += $relative
    }
    if ($scopes.Count -eq 0) { throw "legacy manifest contains no reviewed ownership scopes" }
    return @($scopes | Select-Object -Unique)
}

function Test-CBLegacyCovered($Relative, $Scopes) {
    foreach ($scope in @($Scopes)) {
        if ($Relative -eq $scope -or ($scope.StartsWith('skills/') -and $Relative.StartsWith($scope + '/', [System.StringComparison]::OrdinalIgnoreCase))) {
            return $true
        }
    }
    return $false
}

function Get-CBLegacyOwnedFromScopes($ProfileRoot, $Inventory, $Scopes) {
    $owned = @{}
    foreach ($relative in @($Inventory.Records.Keys | Sort-Object)) {
        if (-not (Test-CBLegacyCovered $relative $Scopes)) { continue }
        $target = Get-CBTargetPath $ProfileRoot $relative
        Assert-CBProfilePath $ProfileRoot $target
        if (-not (Test-Path -LiteralPath $target)) { continue }
        $item = Get-Item -LiteralPath $target -Force
        if ($item.PSIsContainer -or (Test-CBReparsePoint $item)) { throw "reviewed legacy path is missing or replaced: $target" }
        $actual = Get-CBSha256 $target
        if (@($Inventory.Records[$relative] | Where-Object { $_.Sha256 -eq $actual }).Count -eq 0) {
            throw "reviewed legacy file was modified or is unknown: $target"
        }
        $owned[$relative] = $actual
    }
    if ($owned.Count -eq 0) { throw "legacy manifest does not prove ownership of any installed file" }
    return $owned
}

function Get-CBCompleteLegacyRevision($ProfileRoot, $Inventory) {
    $matches = @()
    foreach ($revision in @($Inventory.Revisions)) {
        $candidate = @{}
        $valid = $true
        foreach ($relative in @($Inventory.Records.Keys)) {
            $record = @($Inventory.Records[$relative] | Where-Object { $_.Revision -eq $revision })
            if ($record.Count -ne 1) { $valid = $false; break }
            $target = Get-CBTargetPath $ProfileRoot $relative
            Assert-CBProfilePath $ProfileRoot $target
            if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { $valid = $false; break }
            if ((Get-CBSha256 $target) -ne $record[0].Sha256) { $valid = $false; break }
            $candidate[$relative] = $record[0].Sha256
        }
        if ($valid) { $matches += [PSCustomObject]@{ Revision = $revision; Files = $candidate } }
    }
    if ($matches.Count -eq 0) {
        throw "no complete reviewed legacy installation was found; refusing without ownership proof"
    }
    return $matches[0].Files
}

function Assert-CBOwnedFilesCurrent($ProfileRoot, $Files) {
    foreach ($relative in @($Files.Keys | Sort-Object)) {
        $target = Get-CBTargetPath $ProfileRoot $relative
        Assert-CBProfilePath $ProfileRoot $target
        if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { throw "managed installation file is missing or replaced: $target" }
        if ((Get-CBSha256 $target) -ne $Files[$relative]) { throw "managed installation file was modified: $target" }
    }
}

function New-CBTempDirectory($Prefix) {
    $base = Get-CBFullPath ([System.IO.Path]::GetTempPath())
    Assert-CBNoReparseAbsolutePath $base
    $path = Join-Path $base ($Prefix + [System.Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $path -ErrorAction Stop | Out-Null
    Assert-CBNoReparseAbsolutePath $path
    return $path
}

function Copy-CBFileExclusive($Source, $Destination) {
    $input = [System.IO.File]::Open($Source, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $output = $null
    try {
        $output = [System.IO.File]::Open($Destination, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        $input.CopyTo($output)
        $output.Flush()
    } finally {
        if ($output) { $output.Dispose() }
        $input.Dispose()
    }
}

function Copy-CBBackupSet($ProfileRoot, $RelativePaths, $BackupRoot) {
    $backed = @{}
    foreach ($relative in @($RelativePaths | Sort-Object -Unique)) {
        $target = Get-CBTargetPath $ProfileRoot $relative
        if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { continue }
        $backup = Join-Path $BackupRoot ($relative.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backup) | Out-Null
        Copy-Item -LiteralPath $target -Destination $backup -ErrorAction Stop
        if ((Get-CBSha256 $backup) -ne (Get-CBSha256 $target)) { throw "backup verification failed: $target" }
        $backed[$relative] = $backup
    }
    return $backed
}

function Remove-CBEmptyParents($ProfileRoot, $RelativePaths) {
    $directories = @{}
    foreach ($relative in @($RelativePaths)) {
        $target = Get-CBTargetPath $ProfileRoot $relative
        $directory = Split-Path -Parent $target
        while ((Test-CBPathUnderRoot $directory $ProfileRoot) -and -not (Get-CBFullPath $directory).Equals((Get-CBFullPath $ProfileRoot), [System.StringComparison]::OrdinalIgnoreCase)) {
            $directories[(Get-CBFullPath $directory)] = $true
            $directory = Split-Path -Parent $directory
        }
    }
    foreach ($directory in @($directories.Keys | Sort-Object { $_.Length } -Descending)) {
        Assert-CBProfilePath $ProfileRoot $directory
        if ((Test-Path -LiteralPath $directory -PathType Container) -and -not @(Get-ChildItem -LiteralPath $directory -Force)) {
            Remove-Item -LiteralPath $directory -Force -ErrorAction Stop
        }
    }
}

function Restore-CBTransaction($ProfileRoot, $AllRelative, $Backed, $ManifestPath, $ManifestBackup, $ManageManifest) {
    foreach ($relative in @($AllRelative | Sort-Object -Unique)) {
        $target = Get-CBTargetPath $ProfileRoot $relative
        try {
            Assert-CBProfilePath $ProfileRoot $target
            if (Test-Path -LiteralPath $target -PathType Leaf) { Remove-Item -LiteralPath $target -Force -ErrorAction Stop }
            if ($Backed.ContainsKey($relative)) {
                New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
                Copy-Item -LiteralPath $Backed[$relative] -Destination $target -ErrorAction Stop
            }
        } catch {
            Write-Warning "rollback could not restore $target`: $($_.Exception.Message)"
        }
    }
    if ($ManageManifest) {
        try {
            if (Test-Path -LiteralPath $ManifestPath -PathType Leaf) { Remove-Item -LiteralPath $ManifestPath -Force }
            if ($ManifestBackup) {
                New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ManifestPath) | Out-Null
                Copy-Item -LiteralPath $ManifestBackup -Destination $ManifestPath -ErrorAction Stop
            }
        } catch {
            Write-Warning "rollback could not restore the installation receipt: $($_.Exception.Message)"
        }
    }
}

function Invoke-ClaudeBlogInstall($SourceRoot, $ProfileRoot, $ManifestPath, $LegacyInventoryPath, $Version) {
    $profile = Get-CBFullPath $ProfileRoot
    $manifest = Get-CBFullPath $ManifestPath
    if ((Split-Path -Parent $manifest) -ne $profile -or (Split-Path -Leaf $manifest) -ne 'claude-blog-manifest.txt') {
        throw "unsafe installation receipt path: $manifest"
    }
    Assert-CBNoReparseAbsolutePath (Split-Path -Parent $profile)
    if (Test-Path -LiteralPath $profile) { Assert-CBNoReparseAbsolutePath $profile }
    $sourcePlan = Get-CBSourcePlan $SourceRoot
    $plan = $sourcePlan.Files
    $inventory = Read-CBLegacyInventory $LegacyInventoryPath
    $owned = @{}
    $receiptRaw = $null
    if (Test-Path -LiteralPath $manifest) {
        $receipt = Read-CBReceipt $manifest $profile
        $receiptRaw = $receipt.Raw
        if ($receipt.Kind -eq 'v2') {
            Assert-CBOwnedFilesCurrent $profile $receipt.Files
            $owned = $receipt.Files
        } else {
            $scopes = Get-CBLegacyScopes $receipt.Raw $profile $inventory
            $owned = Get-CBLegacyOwnedFromScopes $profile $inventory $scopes
        }
    }

    foreach ($relative in @($plan.Keys | Sort-Object)) {
        $target = Get-CBTargetPath $profile $relative
        Assert-CBProfilePath $profile $target
        if (-not (Test-Path -LiteralPath $target)) { continue }
        $item = Get-Item -LiteralPath $target -Force
        if ($item.PSIsContainer -or (Test-CBReparsePoint $item)) { throw "installation collision is not a regular file: $target" }
        $actual = Get-CBSha256 $target
        if ($owned.ContainsKey($relative)) {
            if ($actual -ne $owned[$relative]) { throw "managed installation file was modified: $target" }
        } elseif ($actual -eq $plan[$relative].Sha256) {
            continue
        } elseif ($inventory.Records.ContainsKey($relative) -and @($inventory.Records[$relative] | Where-Object { $_.Sha256 -eq $actual }).Count -gt 0) {
            continue
        } else {
            throw "refusing to overwrite an unowned existing file: $target"
        }
    }

    $transactionRoot = New-CBTempDirectory '.claude-blog-windows-install-'
    $stageRoot = Join-Path $transactionRoot 'stage'
    $backupRoot = Join-Path $transactionRoot 'backup'
    New-Item -ItemType Directory -Path $stageRoot, $backupRoot | Out-Null
    $allRelative = @($owned.Keys) + @($plan.Keys)
    $backed = @{}
    $manifestBackup = $null
    $mutationStarted = $false
    try {
        foreach ($relative in @($plan.Keys | Sort-Object)) {
            $staged = Join-Path $stageRoot ($relative.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $staged) | Out-Null
            Copy-Item -LiteralPath $plan[$relative].Source -Destination $staged -ErrorAction Stop
            if ((Get-CBSha256 $staged) -ne $plan[$relative].Sha256) { throw "staged payload hash mismatch: $relative" }
        }
        $backed = Copy-CBBackupSet $profile $allRelative $backupRoot
        if (Test-Path -LiteralPath $manifest -PathType Leaf) {
            $manifestBackupPath = Join-Path $transactionRoot 'previous-receipt'
            Copy-Item -LiteralPath $manifest -Destination $manifestBackupPath -ErrorAction Stop
            $manifestBackup = $manifestBackupPath
        }
        $receiptStage = Join-Path $transactionRoot 'new-receipt'
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($receiptStage, (ConvertTo-CBReceipt $plan $Version), $utf8NoBom)

        $mutationStarted = $true
        New-Item -ItemType Directory -Force -Path $profile | Out-Null
        $copyCount = 0
        foreach ($relative in @($plan.Keys | Sort-Object)) {
            $target = Get-CBTargetPath $profile $relative
            Assert-CBProfilePath $profile $target
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
            Assert-CBProfilePath $profile $target
            $temporary = Join-Path (Split-Path -Parent $target) ('.' + (Split-Path -Leaf $target) + '.claude-blog-' + [System.Guid]::NewGuid().ToString('N'))
            Copy-CBFileExclusive (Join-Path $stageRoot ($relative.Replace('/', [System.IO.Path]::DirectorySeparatorChar))) $temporary
            if ((Get-CBSha256 $temporary) -ne $plan[$relative].Sha256) { throw "commit payload hash mismatch: $relative" }
            if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force -ErrorAction Stop }
            Move-Item -LiteralPath $temporary -Destination $target -ErrorAction Stop
            $copyCount++
            if ($env:CLAUDE_BLOG_TEST_FAIL_AFTER_COPY -and $copyCount -ge [int]$env:CLAUDE_BLOG_TEST_FAIL_AFTER_COPY) {
                throw "injected copy failure"
            }
        }
        foreach ($relative in @($owned.Keys | Where-Object { -not $plan.ContainsKey($_) } | Sort-Object)) {
            $target = Get-CBTargetPath $profile $relative
            Assert-CBProfilePath $profile $target
            if (Test-Path -LiteralPath $target -PathType Leaf) { Remove-Item -LiteralPath $target -Force -ErrorAction Stop }
        }
        Assert-CBProfilePath $profile $manifest
        $manifestTemporary = Join-Path $profile ('.claude-blog-manifest.' + [System.Guid]::NewGuid().ToString('N') + '.tmp')
        Copy-CBFileExclusive $receiptStage $manifestTemporary
        if (Test-Path -LiteralPath $manifest) { Remove-Item -LiteralPath $manifest -Force -ErrorAction Stop }
        Move-Item -LiteralPath $manifestTemporary -Destination $manifest -ErrorAction Stop
    } catch {
        if ($mutationStarted) {
            Restore-CBTransaction $profile $allRelative $backed $manifest $manifestBackup $true
        }
        throw
    } finally {
        Remove-Item -LiteralPath $transactionRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    Remove-CBEmptyParents $profile @($owned.Keys | Where-Object { -not $plan.ContainsKey($_) })
    return [PSCustomObject]@{
        SubSkillCount = @($sourcePlan.SkillNames).Count
        AgentCount = @($sourcePlan.AgentNames).Count
        RootScriptCount = @($sourcePlan.ScriptNames).Count
    }
}

function Invoke-ClaudeBlogUninstall($ProfileRoot, $ManifestPath, $LegacyInventoryPath) {
    $profile = Get-CBFullPath $ProfileRoot
    $manifest = Get-CBFullPath $ManifestPath
    if ((Split-Path -Parent $manifest) -ne $profile -or (Split-Path -Leaf $manifest) -ne 'claude-blog-manifest.txt') {
        throw "unsafe installation receipt path: $manifest"
    }
    Assert-CBNoReparseAbsolutePath (Split-Path -Parent $profile)
    if (-not (Test-Path -LiteralPath $profile -PathType Container)) { throw "Claude profile does not exist: $profile" }
    Assert-CBNoReparseAbsolutePath $profile
    $hasManifest = Test-Path -LiteralPath $manifest
    if ($hasManifest) {
        $receipt = Read-CBReceipt $manifest $profile
        if ($receipt.Kind -eq 'v2') {
            $owned = $receipt.Files
            Assert-CBOwnedFilesCurrent $profile $owned
        } else {
            if (-not $LegacyInventoryPath) { throw "legacy uninstall requires the complete reviewed repository and ownership inventory" }
            $inventory = Read-CBLegacyInventory $LegacyInventoryPath
            $scopes = Get-CBLegacyScopes $receipt.Raw $profile $inventory
            $owned = Get-CBLegacyOwnedFromScopes $profile $inventory $scopes
        }
    } else {
        if (-not $LegacyInventoryPath) { throw "no receipt exists; legacy uninstall requires the complete reviewed repository and ownership inventory" }
        $inventory = Read-CBLegacyInventory $LegacyInventoryPath
        $owned = Get-CBCompleteLegacyRevision $profile $inventory
    }

    foreach ($relative in @($owned.Keys)) {
        $target = Get-CBTargetPath $profile $relative
        Assert-CBProfilePath $profile $target
    }
    if ($hasManifest) { Assert-CBProfilePath $profile $manifest }

    $transactionRoot = New-CBTempDirectory '.claude-blog-windows-uninstall-'
    $backed = @{}
    $manifestBackup = $null
    $mutationStarted = $false
    try {
        $backupRoot = Join-Path $transactionRoot 'backup'
        New-Item -ItemType Directory -Path $backupRoot | Out-Null
        $backed = Copy-CBBackupSet $profile @($owned.Keys) $backupRoot
        if ($hasManifest) {
            $manifestBackupPath = Join-Path $transactionRoot 'previous-receipt'
            Copy-Item -LiteralPath $manifest -Destination $manifestBackupPath -ErrorAction Stop
            $manifestBackup = $manifestBackupPath
        }
        $deleteCount = 0
        foreach ($relative in @($owned.Keys | Sort-Object)) {
            $target = Get-CBTargetPath $profile $relative
            Assert-CBProfilePath $profile $target
            $mutationStarted = $true
            Remove-Item -LiteralPath $target -Force -ErrorAction Stop
            Write-Host "  Removed verified package file: $target" -ForegroundColor Green
            $deleteCount++
            if ($env:CLAUDE_BLOG_TEST_FAIL_AFTER_DELETE -and $deleteCount -ge [int]$env:CLAUDE_BLOG_TEST_FAIL_AFTER_DELETE) {
                throw "injected delete failure"
            }
        }
        if ($hasManifest) { Remove-Item -LiteralPath $manifest -Force -ErrorAction Stop }
    } catch {
        if ($mutationStarted) {
            Restore-CBTransaction $profile @($owned.Keys) $backed $manifest $manifestBackup $hasManifest
        }
        throw
    } finally {
        Remove-Item -LiteralPath $transactionRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    Remove-CBEmptyParents $profile @($owned.Keys)
}
