[CmdletBinding()]
param(
    [string]$HostName = "10.0.5.103",
    [int]$SshPort = 25450,
    [string]$UserName = "root",
    [string]$IdentityFile = "C:\Users\LongShine\.ssh\id_rsa",
    [int]$RemoteSocksPort = 9998,
    [int]$LocalSocksPort = 10808,
    [int]$ReconnectDelaySeconds = 15
)

$ErrorActionPreference = "Stop"

$mutex = [Threading.Mutex]::new(
    $false,
    "Local\EACR_APT_GDrive_Reverse_Tunnel_Watchdog"
)
if (-not $mutex.WaitOne(0)) {
    exit 0
}

$runtimeRoot = Join-Path $env:LOCALAPPDATA "EACR-APT"
$logPath = Join-Path $runtimeRoot "gdrive_reverse_tunnel.log"
[IO.Directory]::CreateDirectory($runtimeRoot) | Out-Null

$ssh = Join-Path $env:SystemRoot "System32\OpenSSH\ssh.exe"
if (-not [IO.File]::Exists($ssh)) {
    $ssh = (Get-Command ssh.exe -ErrorAction Stop).Source
}

$sshArgs = @(
    # Ignore the user's SSH config. Its separate RemoteForward 9999 entry can
    # collide with diagnostic SSH sessions and must not kill this watchdog.
    "-F", "NUL",
    "-N",
    "-T",
    "-o", "BatchMode=yes",
    "-o", "ExitOnForwardFailure=yes",
    "-o", "ConnectTimeout=20",
    "-o", "ServerAliveInterval=30",
    "-o", "ServerAliveCountMax=3",
    "-p", [string]$SshPort,
    "-i", $IdentityFile,
    "-R", "${RemoteSocksPort}:127.0.0.1:${LocalSocksPort}",
    "${UserName}@${HostName}"
)

try {
    while ($true) {
        $startedAt = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
        [IO.File]::AppendAllText(
            $logPath,
            "[$startedAt] starting SSH reverse tunnel remote=$RemoteSocksPort local=$LocalSocksPort`r`n"
        )

        $savedErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        try {
            & $ssh @sshArgs 2>> $logPath
            $exitCode = $LASTEXITCODE
        }
        finally {
            $ErrorActionPreference = $savedErrorActionPreference
        }

        $endedAt = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
        [IO.File]::AppendAllText(
            $logPath,
            "[$endedAt] SSH exited code=$exitCode; retrying in $ReconnectDelaySeconds seconds`r`n"
        )
        Start-Sleep -Seconds $ReconnectDelaySeconds
    }
}
finally {
    $mutex.ReleaseMutex()
    $mutex.Dispose()
}
