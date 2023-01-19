#!/bin/bash
PYTHONENV="/p1mon/p1monenv"

echo "[*] cd $PYTHONENV."
cd $PYTHONENV

echo "[*] activeer python enviroment.(source bin/activate)"
source bin/activate

echo "[*] upgrade PIP."
python3 -m pip install --upgrade pip

echo "[*] maak een lijst van packages met een nieuwere versie, dit duurt even."
python3 -m pip list --outdated 

echo "[*] upgrade met python3 -m pip install --upgrade <met outdated package>"
echo "[*] doe dit manueel!"
echo "[*] deactivate om de pyton enviroment uit te schakelen."
