# Go to your Git repository
Set-Location "C:\Users\DELL\Desktop\Hospital-Readmission-Prediction\bootcamp-ace-26-team-1"

# Switch to the main branch
git switch main

# Get the latest changes from GitHub
git pull origin main

# Stage only the documentation
git add Logs/DOCUMENTATION.docx

# Create a commit with the current date and time
$time = Get-Date -Format "yyyy-MM-dd HH:mm"
git commit -m "Updated Scrum Master Documentation - $time"

# Push to GitHub
git push origin main

Write-Host ""
Write-Host "========================================"
Write-Host " Documentation uploaded successfully!"
Write-Host "========================================"

Pause