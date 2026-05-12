# Features - Tank Survivor

## Idee de base
- Jeu d'action/survie en arene (vue du dessus) : survivre a des vagues d'ennemis qui deviennent plus dangereuses.
- Boucle principale : bouger, tirer, esquiver, recuperer des gemmes XP, choisir des upgrades, battre les boss de palier.
- Systeme de classes : debut de partie avec choix d'une classe qui definit une competence (E) et une ulti (A).

## Gameplay coeur
- Deplacements clavier (`ZQSD`/fleches) et manette (stick + D-pad).
- Tir principal continu avec projectiles multiples selon upgrades.
- Visée souris/manette, avec auto-ciblage de l'ennemi le plus proche quand le joueur ne vise pas.
- Gestion des collisions complete : projectiles, contact, zones, lasers, explosions, invocations.
- Calculs de degats centralises avec statistiques detaillees par source.

## Progression du joueur
- XP via gemmes au sol, niveau qui monte avec palier XP dynamique.
- A chaque niveau :
- `+4` degats de base.
- `+5` PV max (et petit soin instantane).
- Choix d'upgrade parmi 3 cartes (pool standard + pool epique selon conditions).
- Charge d'ulti qui se regenere passivement + gagnee sur kills ennemis.
- Systeme de combo concentration : si aucun degat recu, bonus de degats progressif.

## Systeme de vagues
- Vagues progressives avec nombre d'ennemis qui augmente (`18 + 3 * vague`).
- Spawn en deux temps : une partie immediate, le reste echelonné sur un intervalle.
- Condition de fin de vague : plus d'ennemis hostiles, pas de boss, plus de spawn en attente.
- Transition de fin de vague : aspiration acceleree des gemmes, puis upgrade(s) et vague suivante.
- Tous les 5 niveaux : apparition d'un boss.
- Pendant un combat de boss : spawns additionnels reguliers d'ennemis standards.
- Mort du boss : nettoyage des ennemis restants, pluie massive de gemmes, boost de puissance "post-boss" pour les competences ultimes.

## Ennemis
- 4 archetypes :
- `basic` : profil standard.
- `fast` : tres rapide, peu de PV.
- `tank` : lent, beaucoup de PV, rayon laser charge -> tir.
- `shooter` : tire des projectiles.
- Mise a l'echelle avec la vague : PV/vitesse/pression offensive augmentent.

## Boss
- Boss tous les 5 niveaux, avec grosse reserve de PV.
- Rotation entre 3 patterns :
    - Multi-lasers rotatifs.
    - Salves de projectiles.
    - Zones explosives sur la position du joueur
- les patterns gagnent en intensite selon % de vie

## Classes
- `Maitre des Lasers`
    - Competence : laser spatial apres courte charge, transperce en ligne.
    - Ulti : `Constellations Laser` (reseau de noeuds + segments laser persistants).
- `Maitre de la lame`
    - Competence  : lame geante tirée la ou il y a le plus d'ennemi
    - Ulti  : `Lame Prismatique` (3 lame qui orbite autour du player).
- `Biochimiste fou`
    - Competence : invocations chimiques (ennemis convertis/allies temporaires).
    - Ulti  : `Transmutation Hostile` (conversion de masse des ennemis proches).
- `Maitre des eclats`
    - Competence : zone de degats continue.
    - Ulti  : `Essaim Spectral` (generation d'eclats traqueurs).
- `Maitre des abeilles`
    - Competence : essaim d'abeilles offensif.
    - Ulti  : `Ruche Royale` (ruche durable avec chaines de degats).
- `Maitre spatial`
    - Competence : onde de choc.
    - Ulti  : `Singularite Neon` (trou noir qui attire puis explose).

## Competences, armes et invocations
- Tir principal evolutif (cadence, degats, vitesse projectile, multi-tir).
- Ricochet des projectiles (rebonds intelligents + attenuation).
- Orbes de feu orbitaux (impact + brulure).
- Evolution `Cercle de feu` (anneau de brulure autour du joueur).
- Orbe laser autonome (faisceau periodique sur cibles hostiles).
- Electroelf (familier qui declenche des frappes de foudre zonees).
- Lance-roquettes a verrouillage + explosion de zone.
- Evolution roquettes fragmentation (eclats supplementaires).
- Invocations/allies :
- Conversion d'ennemis en allies (tir, beam tank, contact).
- Ruches qui spawnent des abeilles chasseuses.

## Upgrades
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
- Epiques / evolutions :
- `Orbe laser`
- `Electroelf`
- `EVO: Cercle de feu+`
- `EVO: Rockets fragmentation+`

## Pickups temporaires
- `Shield` : bouclier absorbant.
- `Multishot` : forte augmentation temporaire du nombre de projectiles.
- `Haste` : vitesse + cadence + degats de tir renforces temporairement.
- `Heal` : regeneration temporairement amplifiee.
- Les pickups et gemmes utilisent un comportement magnetique progressif vers le joueur.

## Interface et retours visuels
- HUD complet : PV, cadence/tir, bouclier, roquettes, score, progression de vague/boss.
- Barre XP + niveau.
- Barre ulti (A) + cooldown.
- Barre competence (E) contextuelle selon classe active.
- Affichage des buffs temporaires avec timer visuel.
- Nombres de degats flottants et effets de pulse/explosion/laser/zone.
- Ecrans dedies : menu de depart, selection de classe, choix d'upgrade, game over.
- Panneaux d'analyse de degats (infliges et recus) pendant la partie et en fin de partie.

## Controles principaux
- Deplacement : `ZQSD` / fleches.
- Tir manuel : clic gauche (ou `Espace`) ; sinon tir auto sur cible proche.
- Ulti : touche `A` (ou bouton manette associe).
- Competence de classe : touche `E` (ou bouton manette associe).
- Navigation UI : clavier, souris et manette (selection + validation).
