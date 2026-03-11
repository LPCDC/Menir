# start_tunnel.ps1
# Helper to expose Menir Server to the internet for Google Opal

Write-Host "🚀 Menir Tunnel Launcher" -ForegroundColor Cyan
Write-Host "-------------------------"

# 1. Check if Menir Server is running (optional check, or just remind)
Write-Host "⚠️  Ensure 'menir server' is running in another terminal!" -ForegroundColor Yellow

# 2. Check for cloudflared
if (Get-Command "cloudflared" -ErrorAction SilentlyContinue) {
    Write-Host "✅ Cloudflared (Cloudflare Tunnels) found." -ForegroundColor Green
    Write-Host "Starting tunnel on port 8000..."
    
    # Run cloudflared
    Write-Host "Copy the URL from the output below." -ForegroundColor Magenta
    cloudflared tunnel --url http://127.0.0.1:8000
}
else {
    Write-Host "❌ Cloudflared not found in PATH." -ForegroundColor Red
    Write-Host "Please install cloudflared: 'winget install Cloudflare.cloudflared'"
    Write-Host "Then run: 'cloudflared tunnel --url http://127.0.0.1:8000'"
}
