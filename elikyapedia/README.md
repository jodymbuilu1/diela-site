# ELIKYAPEDIA — édition 2.0

Édition du 10 novembre 2026 : seize articles dans trois domaines (six en Politique, cinq en Économie, cinq en Social).

## Source éditoriale

`articles.json` contient les textes publics relus : résumé de 100 mots, dix points clés, sections détaillées, références et provenance documentaire sans identifiants privés Drive.

`python elikyapedia/build.py` depuis la racine génère :

- le catalogue et les trois portails de domaine ;
- seize articles sous `articles/<slug>/index.html` ;
- seize versions texte sous `textes/<slug>.md` ;
- les pages de sources et de méthode ;
- les pages de continuité depuis les anciennes adresses.

Le générateur valide les effectifs (5 par domaine), la longueur des résumés, les dix points clés, un minimum de six sections et de 1 000 mots de développement par article, et les bornes des appels de références. Il ne vérifie pas à lui seul l'exactitude factuelle : toute modification requiert une relecture des passages et de leurs sources.

`edition.css` et `edition.js` sont autonomes. Aucune bibliothèque, police distante, requête de recherche externe ni compte n'est nécessaire. Le site reste statique sur GitHub Pages, domaine diela.org.

## Corrections

Modifier `articles.json`, vérifier les sources, actualiser les dates de l'édition dans le générateur, régénérer, puis contrôler les liens et la mise en page avant publication. Conserver les slugs et les renvois historiques. Le Git conserve les versions antérieures. Les cahiers PDF v1 restent des archives ; ils ne sont pas l'édition courante.

Les documents Drive demeurent inchangés. Les informations personnelles, instructions, stratégies internes, projections non vérifiées et accusations non sourcées ne doivent pas être publiées. Les documents tiers sont référencés chez leurs éditeurs et ne sont pas redistribués.
