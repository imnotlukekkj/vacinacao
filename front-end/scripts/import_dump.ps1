<#
PowerShell script to import a database dump into the Postgres container used by this project.
Usage:
  .\scripts\import_dump.ps1 -FilePath .\vacinacao_dump.sql
  .\scripts\import_dump.ps1 -FilePath .\vacinacao_dump.dump -ContainerName pg-temp

What it does:

Note: run from project root in PowerShell.
#>
    [Parameter(Mandatory=$true)]
    [string]$FilePath,

    @"
    PowerShell script to import a database dump into the Postgres container used by this project.
    Usage:
      .\scripts\import_dump.ps1 -FilePath .\vacinacao_dump.sql
      .\scripts\import_dump.ps1 -FilePath .\vacinacao_dump.dump -ContainerName pg-temp

    What it does:
    - Detects the Postgres container (or uses provided name)
    - Creates a textual backup before import
    - Copies the dump to the container and restores it (psql or pg_restore)
    - Runs several verification queries and prints results
    - Optionally restarts the backend service

    Note: run from project root in PowerShell.
    "@

    param(
        [Parameter(Mandatory=$true)]
        [string]$FilePath,

        [string]$ContainerName = "pg-temp",

        [switch]$RestartBackend = $false
    )

    function Get-PostgresContainer {
        param([string]$hint)
        $ps = docker ps --format "{{.Names}}\t{{.Image}}\t{{.Ports}}" | Select-String -Pattern "postgres" -AllMatches
        if ($ps) {
            foreach ($line in $ps) {
                $parts = $line -split "\t"
                if ($parts.Length -ge 1) { return $parts[0] }
            }
        }
        return $hint
    }

    # normalize file path
    $absPath = Resolve-Path -Path $FilePath -ErrorAction Stop
    $absPath = $absPath.Path

    if (-not (Test-Path $absPath)) {
        Write-Error "File not found: $absPath"
        exit 1
    }

    $container = Get-PostgresContainer -hint $ContainerName
    Write-Host "Using Postgres container: $container"

    # backup current DB (textual)
    $backupFileHost = Join-Path -Path (Get-Location) -ChildPath "vacinacao_backup_before_import.sql"
    Write-Host "Creating textual backup to: $backupFileHost"
    docker exec -i $container pg_dump -U postgres -d vacinacao > $backupFileHost
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Backup command returned non-zero exit code. Check docker/pg_dump output above."
    }

    # copy file into container
    $dest = "/tmp/$(Split-Path -Leaf $absPath)"
    Write-Host "Copying $absPath -> ${container}:$dest"
    docker cp $absPath "${container}:$dest"
    if ($LASTEXITCODE -ne 0) { Write-Error "docker cp failed"; exit 1 }

    # decide restore method
    $ext = [IO.Path]::GetExtension($absPath).ToLower()
    if ($ext -eq '.sql') {
        Write-Host "Restoring SQL (psql)"
        docker exec -i $container psql -U postgres -d vacinacao -f $dest
        if ($LASTEXITCODE -ne 0) { Write-Error "psql restore failed"; exit 1 }
    } elseif ($ext -eq '.dump' -or $ext -eq '.backup') {
        Write-Host "Restoring custom dump (pg_restore)"
        docker exec -i $container pg_restore -U postgres -d vacinacao $dest
        if ($LASTEXITCODE -ne 0) { Write-Error "pg_restore failed"; exit 1 }
    } else {
        Write-Warning "Unknown extension '$ext' — attempting psql (textual)"
        docker exec -i $container psql -U postgres -d vacinacao -f $dest
        if ($LASTEXITCODE -ne 0) { Write-Error "psql restore failed"; exit 1 }
    }

    # verification queries
    Write-Host "Running verification queries..."
    $queries = @(
        "SELECT COUNT(*) FILTER (WHERE trim(sigla) <> '') AS preenchidas, COUNT(*) AS total FROM distribuicao;",
        "SELECT COALESCE(NULLIF(trim(sigla),''),'(vazio)') AS sigla, COUNT(*) AS cnt, SUM(qtde) AS total_qtde FROM distribuicao GROUP BY sigla ORDER BY total_qtde DESC LIMIT 100;",
        "SELECT SUM(qtde) FROM distribuicao;"
    )

    foreach ($q in $queries) {
        Write-Host "--- Query: $q"
        docker exec -i $container psql -U postgres -d vacinacao -c "$q"
    }

    if ($RestartBackend) {
        Write-Host "Restarting backend service via docker compose"
        docker compose restart backend
    }

    Write-Host "Import finished. Check outputs above for errors and verification results."
