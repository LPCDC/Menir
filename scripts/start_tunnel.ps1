# start_tunnel.ps1
# Helper to expose Menir Server to the internet for Google Opal

Write-Host "🚀 Menir Tunnel Launcher" -ForegroundColor Cyan
Write-Host "-------------------------"

# 1. Check if Menir Server is running (optional check, or just remind)
Write-Host "⚠️  Ensure 'menir server' is running in another terminal!" -ForegroundColor Yellow

# 2. Check for ngrok
if (Get-Command "ngrok" -ErrorAction SilentlyContinue) {
    Write-Host "✅ Ngrok found." -ForegroundColor Green
    Write-Host "Starting tunnel on port 8000..."
    
    # Run ngrok
    Write-Host "Copy the 'Forwarding' URL (https://....ngrok-free.app) from the output below." -ForegroundColor Magenta
    ngrok http 8000
}
else {
    Write-Host "❌ Ngrok not found in PATH." -ForegroundColor Red
    Write-Host "Please install ngrok: 'winget install ngrok' or download from ngrok.com"
    Write-Host "Then run: 'ngrok http 8000'"
}
