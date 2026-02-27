param(
  [string]$InDir = ".\projects\Itau\raw\eml",
  [string]$OutCsv = ".\projects\Itau\derived\timeline.csv"
)

New-Item -ItemType Directory -Path (Split-Path $OutCsv) -Force | Out-Null
$rows = @()

Get-ChildItem $InDir -Filter *.eml -Recurse | ForEach-Object {
  $path = $_.FullName
  $txt  = Get-Content $path -Raw

  function Get-H($name) {
    if ($txt -match "(?im)^\Q$name\E:\s*(.+)$") { return $Matches[1].Trim() } else { return "" }
  }

  $subject = Get-H "Subject"
  $from    = Get-H "From"
  $to      = Get-H "To"
  $date    = Get-H "Date"
  $msgid   = Get-H "Message-ID"
  $auth    = Get-H "Authentication-Results"
  $rcvdspf = Get-H "Received-SPF"
  $dkim    = Get-H "DKIM-Signature"
  $arcres  = Get-H "ARC-Authentication-Results"

  # primeiro Received (topo) e último (base) para janelar o trajeto
  $receivedAll = [regex]::Matches($txt, "(?im)^Received:\s*.+$")
  $receivedTop = if ($receivedAll.Count -gt 0) { $receivedAll[0].Value } else { "" }
  $receivedBot = if ($receivedAll.Count -gt 0) { $receivedAll[$receivedAll.Count-1].Value } else { "" }

  $sha256 = (Get-FileHash -Algorithm SHA256 $path).Hash

  $rows += [pscustomobject]@{
    file         = $_.Name
    path         = $path
    date         = $date
    from         = $from
    to           = $to
    subject      = $subject
    message_id   = $msgid
    received_top = $receivedTop
    received_bot = $receivedBot
    auth_results = $auth
    received_spf = $rcvdspf
    dkim_sig     = if ($dkim) { "present" } else { "" }
    arc_results  = $arcres
    sha256       = $sha256
  }
}

$rows | Sort-Object date | Export-Csv -NoTypeInformation -Encoding UTF8 $OutCsv
Write-Host "OK: $($rows.Count) emails -> $OutCsv"
