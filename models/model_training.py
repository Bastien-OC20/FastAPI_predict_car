import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import  GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
import joblib

# Charger les données
df = pd.read_csv("../data/csv/voitures_aramisauto_cleaned.csv")

# Séparer les caractéristiques catégorielles et numériques
categorical_cols = df.select_dtypes(include=["object"]).columns
numeric_cols = df.select_dtypes(include=["int64", "int32"]).columns.drop("Prix")

# Ajouter la variable binaire 'Prix_binaire'
threshold = df["Prix"].median()
df["Prix_binaire"] = (df["Prix"] > threshold).astype(int)

# Préparation des données pour la régression
X = df.drop(columns=["Prix", "Prix_binaire"])
y = df["Prix"]

# Division des données en ensemble d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Création du préprocesseur avec ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
    ]
)

# Liste des modèles et leurs grilles de paramètres à explorer
models = {
    "Gradient_Boosting": (GradientBoostingRegressor(), {
        "regressor__n_estimators": [500],
        "regressor__learning_rate": [0.2],
        "regressor__max_depth": [5],
        "regressor__min_samples_split": [2],
        "regressor__min_samples_leaf": [1],
        "regressor__max_features": ["sqrt"],
        "regressor__random_state": [42],
    })
}

# Exploration des modèles avec GridSearchCV
results = {}
for model_name, (model, param_grid) in models.items():
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", model)
    ])

    # Création de GridSearchCV
    grid_search = GridSearchCV(estimator=pipeline, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2)

    # Entraîner le modèle avec GridSearchCV
    grid_search.fit(X_train, y_train)

    # Meilleurs paramètres
    best_params = grid_search.best_params_
    print(f"{model_name} - Meilleurs paramètres: {best_params}")

    # Prédire les valeurs sur l'ensemble de test
    y_pred = grid_search.predict(X_test)

    # Calculer les métriques d'évaluation
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    results[model_name] = {"MSE": mse, "R²": r2, "Best Params": best_params}
    print(f"{model_name} - MSE: {mse}, R²: {r2}")

    # Enregistrer le modèle
    joblib.dump(
        grid_search.best_estimator_, f"./pkl/{model_name}_model.pkl"
    )

# Afficher les résultats
results_df = pd.DataFrame(results).T
print(results_df)

# Préparation des données pour la classification
X_classification = df.drop(columns=["Prix", "Prix_binaire"])
y_classification = df["Prix_binaire"]

# Division des données en ensemble d'entraînement et de test
X_train_classification, X_test_classification, y_train_classification, y_test_classification = train_test_split(
    X_classification, y_classification, test_size=0.2, random_state=42
)

# Liste des modèles de classification et leurs grilles de paramètres à explorer
classification_models = {
    "Logistic_Regression": (LogisticRegression(max_iter=1000), {
        "classifier__C": [0.1, 1.0, 10.0],
        "classifier__solver": ["liblinear", "lbfgs"]
    })
}

# Exploration des modèles de classification avec GridSearchCV
classification_results = {}
for model_name, (model, param_grid) in classification_models.items():
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", model)
    ])

    # Création de GridSearchCV
    grid_search = GridSearchCV(estimator=pipeline, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2)

    # Entraîner le modèle avec GridSearchCV
    grid_search.fit(X_train_classification, y_train_classification)

    # Meilleurs paramètres
    best_params = grid_search.best_params_
    print(f"{model_name} - Meilleurs paramètres: {best_params}")

    # Prédire les valeurs sur l'ensemble de test
    y_pred = grid_search.predict(X_test_classification)

    # Calculer les métriques d'évaluation
    accuracy = accuracy_score(y_test_classification, y_pred)
    classification_report_result = classification_report(y_test_classification, y_pred)

    classification_results[model_name] = {"Accuracy": accuracy, "Best Params": best_params}
    print(f"{model_name} - Accuracy: {accuracy}")
    print(f"{model_name} - Rapport de classification:\n{classification_report_result}")

    # Enregistrer le modèle
    joblib.dump(grid_search.best_estimator_, f"./pkl/{model_name}_model.pkl")

# Afficher les résultats de classification
classification_results_df = pd.DataFrame(classification_results).T
print(classification_results_df)
