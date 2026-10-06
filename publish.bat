@echo off
rem Double-click this after editing _data\conferences.csv. It commits the change and pushes it; the site rebuilds in a minute or two.
cd /d "%~dp0"
git add _data/conferences.csv
git commit -m "Update conference list" || echo Nothing changed.
git push
pause
