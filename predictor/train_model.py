import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import PolynomialFeatures, StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import os

save_path = os.path.join(os.path.dirname(__file__), 'trained_models')

os.makedirs(save_path, exist_ok=True)

df = pd.read_csv(os.path.join(os.path.dirname(__file__), '../static/heart.csv'))

median_cholesterol = df['Cholesterol'].median()
df['Cholesterol'] = df['Cholesterol'].replace(0, median_cholesterol)

def preprocessing(df, is_training=True, label_encoders=None):
    categorical_columns = ['Gender', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope']
    
    if is_training:
        label_encoders = {}
        for col in categorical_columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            label_encoders[col] = le
        
        X = df.drop(columns=['HeartDisease'])
        y = df['HeartDisease']
        return X, y, label_encoders
    else:
        for col in categorical_columns:
            if col in label_encoders:
                df[col] = label_encoders[col].transform(df[col])
        return df

X, y, label_encoders = preprocessing(df, is_training=True)

poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
X_poly = poly.fit_transform(X)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_poly)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

best_rf = RandomForestClassifier(
    n_estimators=200, 
    max_depth=15,   
    min_samples_split=2,  
    random_state=42
)
best_rf.fit(X_train, y_train)
y_pred = best_rf.predict(X_test)

accuracy = accuracy_score(y_test, y_pred) * 100
print(f"Model accuracy after tuning: {accuracy}%")
print(classification_report(y_test, y_pred))

joblib.dump(best_rf, os.path.join(save_path, 'best_rf_model.pkl'))
joblib.dump(scaler, os.path.join(save_path, 'scaler.pkl'))
joblib.dump(poly, os.path.join(save_path, 'poly.pkl'))
joblib.dump(label_encoders, os.path.join(save_path, 'label_encoders.pkl'))

with open(os.path.join(save_path, 'model_accuracy.txt'), 'w') as f:
    f.write(str(accuracy))

