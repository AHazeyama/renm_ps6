#!/usr/bin/pwsh
#Requires -Version 7.0
mkdir test1st
cd test1st
New-Item test_11.txt
New-Item test_12.txt
New-Item work_11.txt
New-Item work_12.txt
New-Item dummy_11.txt
New-Item dummy_12.txt
mkdir test2nd
cd test2nd
New-Item test_21.txt
New-Item test_22.csv
New-Item work_21.txt
New-Item work_22.csv
New-Item dummy_11.txt
New-Item dummy_12.txt
cd ..
mkdir test3rd
cd test3rd
New-Item test_31.txt
New-Item test_32.csv
New-Item work_31.txt
New-Item work_32.csv
New-Item dummy_11.txt
New-Item dummy_12.txt
cd ..
mkdir work4th
cd work4th
New-Item work_41.txt
New-Item work_42.txt
cd ../..
# & c_write "Cyan" "`r`n --- Test Environment ----"
Write-Host "`r`n --- Test Environment ---" -Foreground Cyan
tree /f test1st
