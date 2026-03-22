@echo off
setlocal

cd /d C:\Users\Eleve\Documents\Cours\NSI\Codes\Jeu

pyinstaller --onefile --windowed ^
  --add-data "character.png;." ^
  --add-data "drone.png;." ^
  --add-data "dronebleu.png;." ^
  --add-data "fireball.png;." ^
  --add-data "genshin.ttf;." ^
  --add-data "haste.png;." ^
  --add-data "heal.png;." ^
  --add-data "multishot.png;." ^
  --add-data "pleindesoldier.png;." ^
  --add-data "rocket.png;." ^
  --add-data "shield.png;." ^
  --add-data "shieldicon.png;." ^
  --add-data "shooter.png;." ^
  --add-data "tank.png;." ^
  game.py

echo.
echo Build termine. Exe: dist\game.exe
pause
