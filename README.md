# Prédict Car 

### Une application de prédiction des prix des voitures d'occasion utilisant l'IA.

## Introduction

Ce projet est une application de prédiction des prix des voitures d'occasion, conçue dans le cadre de notre formation en développement IA. L'application combine des technologies de machine learning et une interface utilisateur intuitive pour prédire le prix des voitures d'occasion et classifier l'offre comme « Bonne affaire » ou « Mauvaise affaire ». L'application a été construite avec React et FastAPI, et elle utilise des modèles de Random Forest et de régression logistique pour offrir une expérience utilisateur simple mais efficace, tout en fournissant des informations utiles aux utilisateurs pour leurs décisions d'achat.

## Fonctionnalités Principales
1. **Interface Utilisateur Moderne :** Une interface utilisateur construite avec React et stylisée avec Material-UI pour une meilleure expérience utilisateur.
2. **Recherche et Prédiction de Prix :** L'utilisateur peut rechercher le prix d'une voiture d'occasion en fournissant des informations telles que le kilométrage, l'année, la marque, le carburant, la transmission, le modèle et l'état du véhicule. Le modèle Random Forest est utilisé pour prédire le prix, offrant une estimation précise basée sur les caractéristiques fournies.
3. **Classification des offres :** En plus de la prédiction de prix, le modèle de régression logistique permet de classifier l'offre comme « Bonne affaire » ou « Mauvaise affaire », donnant à l'utilisateur un indicateur supplémentaire pour évaluer la qualité de l'offre.
4. **Visualisation des données interactives :** Utilisation de Plotly pour visualiser les données de manière interactive, permettant aux utilisateurs de mieux explorer et comprendre les tendances des prix.
5. **Progression de Prédiction** : Ajout d'une barre de progression visible pendant le calcul de la prédiction pour améliorer l'expérience utilisateur.

## Technologies Utilisées

- **Backend :** FastAPI pour la gestion de l'API et des routes backend, offrant une performance et une flexibilité optimales.
- **Frontend :** React, Material-UI pour une interface utilisateur simple, dynamique, et Plotly pour des graphiques interactifs.
- **Base de données :** SQLAlchemy pour la gestion des utilisateurs et des véhicules, garantissant la fiabilité et la persistance des données.
- **Machine Learning :** Scikit-Learn pour les modèles de prédiction (Random Forest et Régression Logistique), offrant une capacité d'apprentissage supervisé robuste et précise.
- **Autres :** Vite.js pour le développement du frontend.

## Installation

### Prérequis

- **Python 3.8+** doit être installé sur votre système.
- **Pipenv** ou **pip** pour la gestion des dépendances.
- **Base de données SQLite** pour gérer les données utilisateurs et véhicules.
- **Node.js et npm** doivent être installés pour exécuter le frontend.

### Étapes d'Installation

1. **Cloner le dépôt :**

   ```bash
   git clone https://github.com/votre-utilisateur/voitures-occasion.git
   cd voitures-occasion
   ```

2. **Installer les dépendances :**

   ```bash
   pip install -r requirements.txt
   ```
  Pour le frontend :

   ```bash
   npm install
   ```

3. **Initialiser la base de données :**

   ```bash
   python create_db.py
   ```

4. **Entraîner les modèles (si nécessaire) :**
   Si les modèles ne sont pas fournis, utilisez le script d'entraînement pour générer les fichiers `.pkl` :

   ```bash
   python models/training_forest.py
   ```

5. **Lancer l'API FastAPI :**

   ```bash
   uvicorn main:app --reload
   ```

6. **Lancer l'interface React :**

   ```bash
   npm run dev
   ```

## Utilisation

L'application est accessible via le frontend React, qui tourne par défaut sur `http://localhost:5173`. Utilisez le frontend pour accéder aux fonctionnalités de prédiction des prix des voitures et à la classification des offres.

### Prédiction des Voitures d'Occasion

- Renseignez les caractéristiques du véhicule pour obtenir une estimation précise du prix et savoir si l'offre est une bonne ou une mauvaise affaire.

## Schéma de la Base de Données

- **Vehicule** : contient les informations sur les véhicules disponibles dans la base (marque, modèle, année, état, etc.), permettant une analyse approfondie pour chaque recherche de prédiction.

## Architecture du Projet

- **API/** : contient les fichiers backend (FastAPI, modèles, schémas, CRUD) pour gérer les interactions côté serveur.
- **data/** : contient les fichiers de données utilisés pour l'entraînement du modèle, assurant la reproductibilité des prédictions.
- **models/** : contient les fichiers d'entraînement des modèles et les modèles sauvegardés en `.pkl`.
- **notebooks/** : contient les notebooks Jupyter pour l'exploration des données et les essais de modélisation.
- **scripts/** : contient des scripts auxiliaires, comme ceux pour insérer des données dans la base de données ou scraper des informations en ligne.
- **sql/** : contient les scripts SQL pour créer les tables de la base de données.
- **tests/** : contient les tests unitaires pour vérifier la bonne exécution de l'application.
- **voiture-prediction/** : Contient l'interface utilisateur développée avec React.
- **database/** : Fichiers relatifs à la base de données, y compris la configuration de SQLAlchemy.
- **create_db.py** : Script pour initialiser la base de données.


## Documentation de l'API

### Endpoints Disponibles

L'API FastAPI fournit des endpoints pour la prédiction des prix, et la gestion des véhicules. La documentation Swagger est accessible à l'adresse `http://localhost:8000/docs` lorsque le serveur est en cours d'exécution.

## Améliorations Futures

- **Améliorations UX/UI :** Ajout de fonctionnalités plus avancées dans l'interface React, comme des graphiques interactifs et des filtres de recherche.
- **Modèles de Machine Learning :** Exploration d'autres modèles plus avancés pour améliorer la précision des prédictions.
- **Authentification :** Ajouter une authentification plus robuste pour sécuriser l'application.
- **Système de Notification :** Ajouter des notifications push lorsque les prédictions sont prêtes.

## Crédits

- **Équipe de Développement :** Projet réalisé dans le cadre d'une formation en développement IA. Merci à toute l'équipe pour la collaboration, l'engagement et la persévérance tout au long du projet !

  - [Sébastien Rapuzzi](https://rands.netlify.app/).
  - [Yamine Aissani](https://www.linkedin.com/in/yamine-aissani-876514254/).
  - [Mathieu Soussignan](https://www.mathieu-soussignan.com).

- **Images et Logos :** Les images utilisées pour le design de l'application sont libres de droits, contribuant à une interface visuelle attrayante sans compromettre la conformité légale.

---

Merci d'utiliser notre application de prédiction de voitures d'occasion ! N'hésitez pas à nous contacter pour toute suggestion d'amélioration, et nous espérons que notre outil vous aidera à trouver la meilleure affaire possible.
