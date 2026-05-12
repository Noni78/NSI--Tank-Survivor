# Features - Tank Survivor

## Idee de base
- Jeu d'action/survie en arene (vue du dessus) : survivre a des vagues d'ennemis qui deviennent plus dangereuses.
- Boucle principale : bouger, tirer, esquiver, recuperer des gemmes XP, choisir des upgrades, battre les boss de palier.
- Systeme de classes : debut de partie avec choix d'une classe qui definit une competence qui se recharge avec le temps et un ultimate/ulti qui se recharge en tuant des ennemi

## Gameplay coeur
- Deplacements clavier (`ZQSD`/fleches) et manette (stick + D-pad).
- Tir principal continu avec projectiles multiples selon upgrades.
- Visée souris/manette, 
- Gestion des collisions complete : projectiles, contact, zones, lasers, explosions, invocations.
- Calculs de degats centralises avec statistiques detaillees.

## Progression du joueur
- XP via gemmes au sol, niveau qui monte avec palier XP
- A chaque niveau :
- `+4` dégâts de base.
- `+5` PV max.
- Choix d'upgrade parmi 3 cartes
- Charge d'ulti qui se régénère passivement + gagnée sur kills ennemis.

## Système de vagues
- Vagues progressives avec nombre d'ennemis qui augmente (`18 + 3 * vague`).
- Spawn en deux temps : une partie immédiate, le reste échelonné sur un intervalle.
- Condition de fin de vague : plus d'ennemis hostiles, pas de boss, plus de spawn en attente.
- Transition de fin de vague : aspiration accélérée des gemmes, puis upgrade(s) et vague suivante.
- Tous les 5 niveaux : apparition d'un boss.
- Pendant un combat de boss : spawns additionnels réguliers d'ennemis standards.
- Mort du boss : nettoyage des ennemis restants, pluie massive de gemmes, boost de puissance "post-boss" pour les compétences ultimes.

## Ennemis
- 4 archétypes :
- `basic` : profil standard.
- `fast` : très rapide, peu de PV.
- `tank` : lent, beaucoup de PV, rayon laser charge -> tir.
- `shooter` : tire des projectiles.
- Mise a l'échelle avec la vague : PV/vitesse/pression offensive augmentent.

## Boss
- Boss tous les 5 niveaux, avec grosse réserve de PV.
- Rotation entre 3 patterns :
    - Multi lasers rotatifs.
    - Salves de projectiles.
    - Zones explosives sur la position du joueur
- les patterns gagnent en intensité selon % de vie

## Classes
- `Maitre des Lasers`
    - Compétence : laser spatial après courte charge, transperce en ligne.
    - Ulti : `Constellations Laser` (réseau de nœuds + segments laser persistants).
- `Maitre de la lame`
    - Compétence  : lame géante tirée la ou il y a le plus d'ennemi
    - Ulti  : `Lame Prismatique` (3 lame qui orbite autour du player).
- `Biochimiste fou`
    - Compétence : invocations chimiques (ennemis convertis/allies temporaires).
    - Ulti  : `Transmutation Hostile` (conversion de masse des ennemis proches).
- `Maitre des éclats`
    - Compétence : zone de dégâts continue.
    - Ulti  : `Essaim Spectral` (génération d'éclats traqueurs).
- `Maitre des abeilles`
    - Compétence : essaim d'abeilles offensif (30 abeilles).
    - Ulti  : `Ruche Royale` (ruche qui reste 30).
- `Maitre spatial`
    - Compétence : onde de choc.
    - Ulti  : `Singularite` (trou noir qui attire les ennemis en faisant des dégâts AOE).

## Compétences, armes 
- Tir principal qui peut s'améliorer avec plusieurs upgrade (cadence, dégâts, vitesse projectile, multi-tir).
- Ricochet des projectiles (rebonds intelligents + atténuation).
- Orbes de feu orbitant autour du player (impact + brulure).
- Evolution `Cercle de feu` (anneau de brulure autour du joueur).
- Orbe laser autonome (faisceau périodique sur ennemis).
- Electroelf (familier qui declenche des frappes de foudre AOE).
- Lance-roquettes a verrouillage + explosion de zone.
- Evolution roquettes fragmentation (éclats supplémentaires).
- Concentration (les dégâts augmentent avec le temps si aucun dégâts reçu)

## Upgrades (liste avec les noms exacts dans le jeu)
- Standards :
- `Vitesse`
- `Proj Speed`
- `Degats`
- `PV Max`
- `Cadence`
- `Multi-tir`
- `Ricochet`
- `Combo concentration`
- `Orbe de feu`
- `Bouclier`
- `Lance roquette`
- Epiques / évolutions :
- `Orbe laser`
- `Electroelf`
- `EVO: Cercle de feu+`
- `EVO: Rockets fragmentation+`

## Pickups temporaires
- `Shield` : bouclier absorbant.
- `Multishot` : forte augmentation temporaire du nombre de projectiles.
- `Haste` : vitesse + cadence + dégâts de tir renforces temporairement.
- `Heal` : régénération temporairement amplifiée.
- Les pickups et gemmes sont drop par les ennemis a leur mort

## Interface et retours visuels
- HUD complet : PV, cadence/tir, bouclier, roquettes, score, progression de vague/boss.
- Barre XP + niveau.
- Barre ulti (A) + cooldown.
- Barre compétence (E) contextuelle selon classe active.
- Affichage des buffs temporaires avec timer visuel (upgrade pickup).
- Nombres de dégâts flottants et effets de pulse/explosion/laser/zone.
- Ecrans dédies : menu de départ, sélection de classe, choix d'upgrade, game over.
- Panneaux d'analyse de dégâts (infliges et reçus) pendant la partie et en fin de partie.

## Controles principaux
- Deplacement : `ZQSD` / fleches / joystick gauche.
- Tir manuel : clic gauche (ou `Espace`) ; sinon tir auto sur cible proche.
- Ulti : touche `A` (ou bouton manette associe).
- Competence de classe : touche `E` (ou bouton manette associe).
- Navigation UI : clavier, souris et manette (selection + validation).
