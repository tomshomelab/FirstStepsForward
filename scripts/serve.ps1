# Tiny static-file server for local preview only (no Python needed).
# Mirrors what nginx will do in Docker:
#   /             → public/index.html
#   /about.html   → public/about.html
#   /assets/...   → assets/...
# Not for production. Press Ctrl+C to stop.

$port = 8094
$root = (Resolve-Path "$PSScriptRoot\..").Path
$publicDir = Join-Path $root "public"
$assetsDir = Join-Path $root "assets"

$mime = @{
  ".html" = "text/html; charset=utf-8"
  ".htm"  = "text/html; charset=utf-8"
  ".css"  = "text/css; charset=utf-8"
  ".js"   = "application/javascript; charset=utf-8"
  ".json" = "application/json; charset=utf-8"
  ".svg"  = "image/svg+xml"
  ".png"  = "image/png"
  ".jpg"  = "image/jpeg"
  ".jpeg" = "image/jpeg"
  ".gif"  = "image/gif"
  ".webp" = "image/webp"
  ".ico"  = "image/x-icon"
  ".woff" = "font/woff"
  ".woff2"= "font/woff2"
  ".txt"  = "text/plain; charset=utf-8"
}

function Resolve-RequestPath([string]$urlPath) {
  $clean = $urlPath.TrimStart('/')
  if ([string]::IsNullOrEmpty($clean)) { return (Join-Path $publicDir "index.html") }

  if ($clean.StartsWith("assets/")) {
    return (Join-Path $root $clean)
  }

  $direct = Join-Path $publicDir $clean
  if (Test-Path $direct -PathType Leaf) { return $direct }

  if (-not [System.IO.Path]::HasExtension($clean)) {
    $withHtml = Join-Path $publicDir ($clean + ".html")
    if (Test-Path $withHtml -PathType Leaf) { return $withHtml }
  }

  return $direct
}

$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Prefixes.Add("http://127.0.0.1:$port/")

try {
  $listener.Start()
  Write-Host "Serving from $root on http://localhost:$port/"
  Write-Host "Public:  $publicDir"
  Write-Host "Assets:  $assetsDir"
  Write-Host "Ctrl+C to stop."

  while ($listener.IsListening) {
    $ctx = $listener.GetContext()
    $req = $ctx.Request
    $res = $ctx.Response
    try {
      $file = Resolve-RequestPath $req.Url.LocalPath
      if (Test-Path $file -PathType Leaf) {
        $ext = [System.IO.Path]::GetExtension($file).ToLower()
        if ($mime.ContainsKey($ext)) { $res.ContentType = $mime[$ext] }
        else { $res.ContentType = "application/octet-stream" }
        $bytes = [System.IO.File]::ReadAllBytes($file)
        $res.ContentLength64 = $bytes.Length
        $res.OutputStream.Write($bytes, 0, $bytes.Length)
        Write-Host ("{0} {1} -> {2}" -f $req.HttpMethod, $req.Url.LocalPath, $file)
      } else {
        $res.StatusCode = 404
        $msg = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found: $($req.Url.LocalPath)")
        $res.ContentType = "text/plain"
        $res.OutputStream.Write($msg, 0, $msg.Length)
        Write-Host ("404 {0}" -f $req.Url.LocalPath)
      }
    } catch {
      Write-Host ("ERR {0}: {1}" -f $req.Url.LocalPath, $_.Exception.Message)
      try { $res.StatusCode = 500 } catch {}
    } finally {
      $res.Close()
    }
  }
} finally {
  if ($listener.IsListening) { $listener.Stop() }
  $listener.Close()
}
