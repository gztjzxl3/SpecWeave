#Requires -Version 7.4
#!/usr/bin/env pwsh
<#
.SYNOPSIS
检测并清理 git 子模块中的陈旧锁文件（index.lock 等）。

.DESCRIPTION
扫描 <RepoRoot>/.git/modules/**/*.lock（各子模块的 git 目录），可选扫描根仓库自身的 .git/*.lock。

按以下规则判定锁状态：
  - ACTIVE     : 文件较新且存在匹配的 git 进程，禁止清理
  - STALE      : 文件年龄 >= -StaleMinutes 分钟，视为陈旧，可安全清理
  - SUSPICIOUS : 文件较新但找不到匹配的 git 进程（孤儿锁，进程已退出），建议确认后清理

默认只检测列出；加 -Clean 才删除 STALE；SUSPICIOUS 需要 -Force 才会删除。
删除操作默认需要交互确认，加 -Force 跳过确认。

.PARAMETER RepoRoot
目标仓库根目录，默认当前工作目录。

.PARAMETER StaleMinutes
陈旧锁阈值（分钟），默认 30。

.PARAMETER Clean
执行清理（默认仅检测列出）。

.PARAMETER Force
跳过清理确认，并允许清理 SUSPICIOUS 锁。

.PARAMETER IncludeRoot
同时扫描根仓库自身的 .git/*.lock。

.EXAMPLE
pwsh .agents/scripts/git-clean-stale-locks.ps1

.EXAMPLE
pwsh .agents/scripts/git-clean-stale-locks.ps1 -Clean

.EXAMPLE
pwsh .agents/scripts/git-clean-stale-locks.ps1 -Clean -StaleMinutes 5 -Force
#>
[CmdletBinding()]
param(
    [string]$RepoRoot = (Get-Location),
    [int]$StaleMinutes = 30,
    [switch]$Clean,
    [switch]$Force,
    [switch]$IncludeRoot
)

$ErrorActionPreference = 'Stop'

function Resolve-GitDir {
    param([string]$Root)

    $dotGit = Join-Path $Root '.git'
    if (Test-Path $dotGit -PathType Container) {
        return $dotGit
    }
    if (Test-Path $dotGit -PathType Leaf) {
        $content = Get-Content $dotGit -TotalCount 1 -ErrorAction SilentlyContinue
        if ($content -match '^gitdir:\s*(.+)$') {
            $gd = $Matches[1].Trim()
            if (-not [System.IO.Path]::IsPathRooted($gd)) {
                $gd = Join-Path $Root $gd
            }
            return (Resolve-Path $gd).Path
        }
    }
    return $null
}

$repoRoot = (Resolve-Path $RepoRoot).Path
$gitDir = Resolve-GitDir -Root $repoRoot
if (-not $gitDir) {
    Write-Host "[git-clean-stale-locks] 未找到 git 仓库: $repoRoot" -ForegroundColor Red
    exit 1
}

$modulesDir = Join-Path $gitDir 'modules'
$locks = @()
if (Test-Path $modulesDir) {
    $locks += @(Get-ChildItem -Path $modulesDir -Recurse -Filter '*.lock' -File -ErrorAction SilentlyContinue)
}
if ($IncludeRoot) {
    $locks += @(Get-ChildItem -Path $gitDir -Filter '*.lock' -File -ErrorAction SilentlyContinue)
}

if ($locks.Count -eq 0) {
    Write-Host "[git-clean-stale-locks] 未发现任何 .lock 文件，一切正常。" -ForegroundColor Green
    exit 0
}

# 收集 git 进程命令行（仅 Windows 可获取；非 Windows 退化为纯年龄判定）
$gitProcLines = @()
if ($IsWindows) {
    $gitProcLines = @(
        Get-CimInstance Win32_Process -Filter "Name='git.exe'" -ErrorAction SilentlyContinue |
            Where-Object { $_.CommandLine } |
            ForEach-Object { ($_.CommandLine -replace '\\', '/').ToLowerInvariant() }
    )
}

$now = Get-Date
$toClean = @()
$staleOrSuspiciousFound = $false
$uncleaned = $false
$cleanFailed = $false
$cancelled = $false

Write-Host ""
Write-Host "=== Git 锁文件检测（RepoRoot=$repoRoot, StaleMinutes=$StaleMinutes）===" -ForegroundColor Cyan
Write-Host "    共发现 $($locks.Count) 个 .lock 文件"

foreach ($lock in $locks) {
    $ageMin = [math]::Round(($now - $lock.LastWriteTime).TotalMinutes, 1)
    $lockDir = ($lock.Directory.FullName -replace '\\', '/').ToLowerInvariant()
    $subWorkPath = ''
    if ($lock.FullName.StartsWith($modulesDir, [System.StringComparison]::OrdinalIgnoreCase)) {
        $relPath = $lock.FullName.Substring($modulesDir.Length).TrimStart('\', '/')
        if ($relPath -match '^(.*)/[^/]+\.lock$') {
            $sub = $Matches[1]
            $subWorkPath = ((Join-Path $repoRoot $sub) -replace '\\', '/').ToLowerInvariant()
        }
    }

    $held = $false
    foreach ($line in $gitProcLines) {
        if ($line.Contains($lockDir) -or ($subWorkPath -and $line.Contains($subWorkPath))) {
            $held = $true
            break
        }
    }

    if ($ageMin -ge $StaleMinutes) {
        $verdict = 'STALE'
    }
    elseif ($held) {
        $verdict = 'ACTIVE'
    }
    else {
        $verdict = 'SUSPICIOUS'
    }

    $color = switch ($verdict) {
        'STALE'      { 'Yellow' }
        'ACTIVE'     { 'Green' }
        'SUSPICIOUS' { 'Magenta' }
    }
    Write-Host ("  [{0,-10}] {1,8} 分钟  {2}" -f $verdict, $ageMin, $lock.FullName) -ForegroundColor $color

    if ($verdict -eq 'ACTIVE') {
        continue
    }

    $staleOrSuspiciousFound = $true
    if ($verdict -eq 'STALE') {
        if ($Clean) {
            $toClean += $lock
        }
        else {
            $uncleaned = $true
        }
    }
    else {
        if ($Clean -and $Force) {
            $toClean += $lock
        }
        else {
            $uncleaned = $true
        }
    }
}

if ($toClean.Count -gt 0) {
    $doClean = $Force
    if (-not $doClean) {
        Write-Host ""
        Write-Host "即将删除 $($toClean.Count) 个陈旧/可疑锁文件："
        foreach ($lock in $toClean) {
            Write-Host "  - $($lock.FullName)" -ForegroundColor Gray
        }
        Write-Host "确认删除？(输入 YES 继续，其他输入取消)" -ForegroundColor Yellow
        $answer = Read-Host
        $doClean = ($answer -eq 'YES')
        if (-not $doClean) {
            $cancelled = $true
        }
    }

    if ($doClean) {
        foreach ($lock in $toClean) {
            try {
                Remove-Item $lock.FullName -Force -ErrorAction Stop
                Write-Host "  已删除: $($lock.FullName)" -ForegroundColor Green
            }
            catch {
                Write-Host "  删除失败: $($lock.FullName) -> $_" -ForegroundColor Red
                $cleanFailed = $true
            }
        }
    }
}

Write-Host ""
if (-not $staleOrSuspiciousFound) {
    Write-Host "[git-clean-stale-locks] 所有锁文件均处于活动状态，未发现陈旧锁。" -ForegroundColor Green
    exit 0
}
if ($uncleaned -or $cancelled -or $cleanFailed) {
    Write-Host "[git-clean-stale-locks] 仍有陈旧/可疑锁文件未清理。" -ForegroundColor Yellow
    Write-Host "    提示：确认无 git 进程运行后，可执行：pwsh $PSCommandPath -Clean -StaleMinutes $StaleMinutes" -ForegroundColor Gray
    exit 1
}
Write-Host "[git-clean-stale-locks] 陈旧/可疑锁文件已全部清理完毕。" -ForegroundColor Green
exit 0