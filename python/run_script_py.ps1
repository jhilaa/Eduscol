param (
    [string]$scriptPath
)

# Supprimer le préfixe .\ ou ./ s'il existe
$cleanPath = $scriptPath -replace '^[.\\\/]+', ''

# Supprimer l'extension .py
$modulePath = $cleanPath -replace '\.py$', ''

# Remplacer les \ ou / par des points
$moduleName = $modulePath -replace '[\\/]', '.'

# Aller dans le dossier racine du projet
$projectRoot = "D:\Utilisateurs\julie\Dropbox\Projets\19 Eduscol\python"
Set-Location $projectRoot

# Exécuter le module
Write-Host "▶️ Lancement du module Python : $moduleName"
python -m $moduleName
