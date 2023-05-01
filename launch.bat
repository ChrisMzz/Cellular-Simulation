@echo off
setlocal EnabledeLayedExpansion

cls
title Compiler

:: prep the folders
cd src
if exist dump (
	del /s /q dump
	cd dump
	rmdir blurred
	cd ..
	rmdir dump
)
if not exist "dump" mkdir dump
cd dump
mkdir blurred
cd ..


set name=1
:nameset
if exist anim%name% (
    set /a name=%name%+1
    goto nameset
)
echo %name%>name.txt


python video.py
python compiler.py
del name.txt

