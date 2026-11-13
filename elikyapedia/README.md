# ELIKYAPEDIA — édition 2.0

Édition du 13 novembre 2026 : dix-neuf articles dans trois domaines (sept en Politique, six en Économie, six en Social), dont un premier article territorial sur la gestion des déchets à Kinshasa.

## Source éditoriale

`articles.json` contient les textes publics relus : résumé de 100 mots, dix points clés, sections détaillées, références et provenance documentaire sans identifiants privés Drive.

`python elikyapedia/build.py` depuis la racine génère :

- le catalogue et les trois portails de domaine ;
- les articles sous `articles/<slug>/index.html` ;
- les versions texte sous `textes/<slug>.md` ;
- les pages de sources et de méthode ;
- les pages de continuité depuis les anciennes adresses.

Le générateur valide les effectifs (au moins cinq par domaine), la longueur des résumés, les dix points clés, un minimum de six sections et de 1 000 mots de développement par article, et les bornes des appels de références. Il ne vérifie pas à lui seul l'exactitude factuelle : toute modification requiert une relecture des passages et de leurs sources.

`edition.css` et `edition.js` sont autonomes. Aucune bibliothèque, police distante, requête de recherche externe ni compte n'est nécessaire. Le site reste statique sur GitHub Pages, domaine diela.org.

## Corrections

Modifier `articles.json`, vérifier les sources, actualiser les dates de l'édition dans le générateur, régénérer, puis contrôler les liens et la mise en page avant publication. Conserver les slugs et les renvois historiques. Le Git conserve les versions antérieures. Les cahiers PDF v1 restent des archives ; ils ne sont pas l'édition courante.

Les documents Drive demeurent inchangés. Les informations personnelles, instructions, stratégies internes, projections non vérifiées et accusations non sourcées ne doivent pas être publiées. Les documents tiers sont référencés chez leurs éditeurs et ne sont pas redistribués.

Les articles spécialisés peuvent identifier leur article général par `parentSlug`. Les liens internes contextuels utilisent `[libellé](/elikyapedia/articles/slug/)` ; le générateur vérifie que les destinations existent dans le catalogue. Les liens internes facilitent la navigation et ne remplacent pas les références documentaires.

## Clarté pour le lecteur

- Chaque résumé et chaque point clé doit se comprendre isolément.
- Expliquer ce qui se passe avant de donner le nom d’un mécanisme ou d’un document.
- Définir les termes techniques et les sigles à la première utilisation.
- Accompagner les chiffres de leur sens, de leur période et de ce qui est mesuré.
- Réserver les précisions documentaires longues aux références ; conserver leurs appels au passage.
- Préserver les incertitudes utiles, sans transformer chaque phrase en avertissement abstrait.
- Vérifier après reformulation que le lecteur peut dire ce qu’il vient d’apprendre.
