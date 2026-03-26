# Lancer le projet

Ce fichier explique comment exécuter le jeu Tank Survivor.

## 1. Contrainte de version Python
- Version recommandee : `Python 3.13.7` (version utilisee pour les tests du projet).
- Version conseillee : `Python 3.10+`.

## 2. Prerequis
- Avoir `python` et `pip` installes.
- Se placer dans le dossier racine du projet (celui qui contient `main.py`).

## 3. Installation des dependances
Commande recommandee :

```bash
pip install -r requirements.txt
```

## 4. Lancement du jeu
Depuis le dossier racine du projet :

```bash
python main.py
```

## 5. Option conseillee : environnement virtuel
Sur Windows :

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
## 6. Pour faire des tests:
En appuyant sur la touche O, cela ouvre une interface "admin" pour se rajouter divers upgrade 