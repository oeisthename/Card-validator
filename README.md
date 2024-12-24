# Validation des Cartes Bancaires et Détection de Fraude

## Description
Ce projet propose une solution complète pour la validation des cartes bancaires et la détection de fraude, en combinant algorithmes avancés, analyse des données et stockage sécurisé. Développé en Python, cet outil pratique s'adresse à tous ceux qui souhaitent renforcer la sécurité des transactions numériques.

## Fonctionnalités
- **Validation des numéros de cartes** : Utilisation de l'algorithme de Luhn pour vérifier la validité des cartes bancaires.
- **Recherche et analyse des BIN** : Intégration d'une API pour obtenir des informations complémentaires sur les BIN et calculer leur entropie afin de détecter les anomalies.
- **Détection de fraude** : Identification des BIN suspects basée sur une plage d'entropie prédéfinie.
- **Stockage sécurisé des données** : Sauvegarde des BIN et de leurs informations dans une base SQLite avec hachage SHA-256.
- **Interface graphique intuitive** : Développée avec Tkinter, l'interface offre une expérience utilisateur simple et conviviale.

## Technologies Utilisées
- **Python** : Langage principal pour le développement du projet.
- **Tkinter** : Bibliothèque pour la création de l'interface graphique.
- **SQLite** : Base de données intégrée pour le stockage des BIN.
- **API BIN Lookup** : Pour obtenir des informations en temps réel sur les BIN.
- **Hachage SHA-256** : Pour garantir la confidentialité des données.

## Prérequis
- **Python 3.8+**
- Les bibliothèques suivantes doivent être installées :
  - `tkinter`
  - `sqlite3`
  - `requests`
  - `pandas`
  - `hashlib`

## Installation
1. Clonez le dépôt :
   ```bash
   git clone  https://github.com/oeisthename/Card-validator/.git
   ```
2. Naviguez dans le répertoire du projet :
   ```bash
   cd Card-validator
   ```
3. Installez les dépendances nécessaires :
   ```bash
   pip install -r requirements.txt
   ```
4. Lancez l'application :
   ```bash
   python c.py
   ```

## Utilisation
1. **Valider une carte bancaire** :
   - Saisissez un numéro de carte bancaire dans le champ prévu.
   - Cliquez sur "Validate Card" pour vérifier sa validité.

2. **Vérifier les BIN** :
   - Entrez les six premiers chiffres de la carte.
   - Cliquez sur "BIN Lookup" pour afficher les informations associées et détecter les anomalies potentielles.

3. **Afficher les données sauvegardées** :
   - Consultez les informations enregistrées via l’interface graphique ou directement dans la base SQLite.

## Structure du Projet
- **`c.py`** : Fichier principal contenant les fonctions de validation, analyse et l'interface graphique.
- **`data.py`** : Outil pour afficher les données enregistrées dans la base SQLite.
- **`requirements.txt`** : Liste des dépendances nécessaires.

## Fonctionnalités Futures
- Intégration du chiffrement RSA pour une sécurité accrue.
- Adoption de l’apprentissage automatique pour détecter les schémas frauduleux.

## Contribution
Les contributions sont les bienvenues ! Si vous avez des idées d’amélioration ou des fonctionnalités à ajouter, n’hésitez pas à créer une issue ou à soumettre une pull request.

## Auteur
**Othmane El Mqiddem**

## Licence
Ce projet est sous licence MIT. Consultez le fichier `LICENSE` pour plus de détails.


