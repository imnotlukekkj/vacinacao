<#
PowerShell script to import a SQL dump into a Postgres database (Supabase or any remote Postgres)
This script does NOT use Docker. It requires `psql` and/or `pg_restore` available in PATH.

Usage:
  .\scripts\import_to_supabase.ps1 -FilePath .\dados.sql -DatabaseUrl "postgresql://user:pass@host:5432/db?sslmode=require"

Parameters:
  -FilePath   : path to .sql (text) or .dump/.backup (custom) file
  -DatabaseUrl: optional, if omitted the script will try to read backend/.env and use DATABASE_URL
  -SkipBackup : switch, when set the script will NOT create a textual backup of the target DB
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath,

    [string]$DatabaseUrl = $null,

    [switch]$SkipBackup = $false
)

function Read-DatabaseUrlFromEnv {
    $envFile = Join-Path -Path (Resolve-Path -Path "..\backend" -ErrorAction SilentlyContinue).Path -ChildPath ".env"
    if (-not (Test-Path $envFile)) {
        return $null
    }
    $content = Get-Content $envFile -Raw
    foreach ($line in $content -split "\n") {
        $l = $line.Trim()
        if ($l -match '^DATABASE_URL\s*=\s*(.+)$') {
            return $Matches[1].Trim()
        }
    }
    return $null
}

# Resolve database URL
if (-not $DatabaseUrl) {
    $dburl = Read-DatabaseUrlFromEnv
    if (-not $dburl) {
        Write-Error "DATABASE_URL not provided and not found in backend/.env. Provide -DatabaseUrl or create backend/.env"
        exit 1
    }
    $DatabaseUrl = $dburl
}

# Resolve path
$absPath = Resolve-Path -Path $FilePath -ErrorAction Stop
$absPath = $absPath.Path
if (-not (Test-Path $absPath)) {
    Write-Error "File not found: $absPath"
    exit 1
}

# Optional textual backup (psql must be available in PATH)
if (-not $SkipBackup) {
    $backupFile = Join-Path -Path (Get-Location) -ChildPath "vacinacao_backup_before_import.sql"
    Write-Host "Creating textual backup to: $backupFile"
    $dumpCmd = "pg_dump --dbname=`"$DatabaseUrl`" --schema=public --format=p --no-owner --no-privileges -f `"$backupFile`""
    Write-Host $dumpCmd
    $proc = Start-Process -FilePath "pg_dump" -ArgumentList "--dbname=$DatabaseUrl","--schema=public","--format=p","--no-owner","--no-privileges","-f","$backupFile" -NoNewWindow -Wait -PassThru
    if ($proc.ExitCode -ne 0) {
        Write-Warning "pg_dump exited with code $($proc.ExitCode). Proceeding may overwrite data."
    }
}

# Decide restore method
$ext = [IO.Path]::GetExtension($absPath).ToLower()
if ($ext -eq '.sql') {
    Write-Host "Restoring SQL (psql) to: $DatabaseUrl"
    $proc = Start-Process -FilePath "psql" -ArgumentList "$DatabaseUrl","-f","$absPath" -NoNewWindow -Wait -PassThru
    if ($proc.ExitCode -ne 0) { Write-Error "psql restore failed (exit $($proc.ExitCode))"; exit 1 }
} elseif ($ext -eq '.dump' -or $ext -eq '.backup') {
    Write-Host "Restoring custom dump (pg_restore) to: $DatabaseUrl"
    $proc = Start-Process -FilePath "pg_restore" -ArgumentList "--verbose","--clean","--no-acl","--no-owner","--dbname=$DatabaseUrl","$absPath" -NoNewWindow -Wait -PassThru
    if ($proc.ExitCode -ne 0) { Write-Error "pg_restore failed (exit $($proc.ExitCode))"; exit 1 }
} else {
    Write-Host "Unknown extension '$ext' — attempting psql textual restore"
    $proc = Start-Process -FilePath "psql" -ArgumentList "$DatabaseUrl","-f","$absPath" -NoNewWindow -Wait -PassThru
    if ($proc.ExitCode -ne 0) { Write-Error "psql restore failed (exit $($proc.ExitCode))"; exit 1 }
}

# Verification queries
Write-Host "Running verification queries..."
$queries = @(
    "SELECT COUNT(*) FILTER (WHERE trim(sigla) <> '') AS preenchidas, COUNT(*) AS total FROM public.distribuicao;",
    "SELECT COALESCE(NULLIF(trim(sigla),''),'(vazio)') AS sigla, COUNT(*) AS cnt, SUM(qtde) AS total_qtde FROM public.distribuicao GROUP BY sigla ORDER BY total_qtde DESC LIMIT 100;",
    "SELECT SUM(qtde) FROM public.distribuicao;"
)

foreach ($q in $queries) {
    Write-Host "--- Query: $q"
    $proc = Start-Process -FilePath "psql" -ArgumentList "$DatabaseUrl","-c","$q" -NoNewWindow -Wait -PassThru
}

Write-Host "Import finished. Check outputs above for errors and verification results."