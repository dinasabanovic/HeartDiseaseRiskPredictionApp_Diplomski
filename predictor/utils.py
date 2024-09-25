from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from imblearn.over_sampling import SMOTE
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report



def preprocessing(df, is_training=True, label_encoders=None):
    categorical_columns = {
        'Gender': ['M', 'F'],
        'ChestPainType': ['TA', 'ATA', 'NAP', 'ASY'],
        'RestingECG': ['Normal', 'ST', 'LVH'],
        'ExerciseAngina': ['Y', 'N'],
        'ST_Slope': ['Up', 'Flat', 'Down']
    }
    
    if 'Cholesterol' in df.columns:
        df['Cholesterol'] = df['Cholesterol'].replace(0, df['Cholesterol'].median())
    
    if is_training:
        label_encoders = {}
        for col, categories in categorical_columns.items():
            if col not in df.columns:
                raise ValueError(f"Column '{col}' is missing from the DataFrame.")
            
            le = LabelEncoder()
            le.fit(categories)  
            df[col] = le.transform(df[col])
            label_encoders[col] = le
        
        if 'HeartDisease' in df.columns:
            X = df.drop(columns=['HeartDisease'])
            y = df['HeartDisease'].apply(lambda x: 1 if x == "have" else 0)  
        else:
            raise ValueError("The 'HeartDisease' column is missing from the training data.")
        
        return X, y, label_encoders
    
    else:
        for col in categorical_columns:
            if col in label_encoders:
                if col not in df.columns:
                    raise ValueError(f"Column '{col}' is missing from the DataFrame.")
                df[col] = label_encoders[col].transform(df[col])
        
        return df
        

def get_recommendations(latest_prediction):
    recommendations = []
    
    if latest_prediction.heart_disease_risk == 'have':
        if latest_prediction.cholesterol > 200:
            recommendations.append("Heart-healthy diet and regular moderate-intensity exercise" 
                                   "recommended.")
        if latest_prediction.restingbp > 130:
            recommendations.append("Regularly monitor your blood pressure and adopt lifestyle" 
                                   "changes.")
        if latest_prediction.fastingbs == 1:
            recommendations.append("Balanced diet, regular exercise and further medical evaluation" 
                                   "for diabetes recommended.")
        if latest_prediction.exerciseangina == 'Y':
            recommendations.append("Avoid strenuous activities until further evaluation is completed.")
        if latest_prediction.chest_pain_type != 'ASY' or latest_prediction.restingecg != 'Normal' or \
           latest_prediction.oldpeak > 1 or latest_prediction.st_slope != 'Flat':
            recommendations.append("Further medical evaluation needed.")
    else:
        recommendations.append("The patient is okay with no significant risks detected.")

    return recommendations








