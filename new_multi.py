import pandas as pd

# Load the dataset
file_path = "E:\Projects\Capstone\Final\Data\masterdatasubset.csv"  # Replace with your dataset path
data = pd.read_csv(file_path)

# Specify the columns to include
exclusive_labels = ['IAT', 'Tot sum', 'Tot size', 'Max', 'Header_Length', 'AVG', 'Magnitue', 
                    'Min', 'rst_count', 'Protocol Type', 'flow_duration', 'Std', 'Radius', 
                    'Variance', 'urg_count', 'Covariance', 'syn_count', 'Number', 'Weight', 'label']

# Filter the dataset to include only the specified columns
filtered_data = data[exclusive_labels]

n_samples = 10000

# Group by the 'label' column and sample
sampled_data = filtered_data.groupby('label', group_keys=False).apply(lambda x: x.sample(n=min(len(x), n_samples)))

# Reset index for the sampled dataset
sampled_data = sampled_data.reset_index(drop=True)

from sklearn.ensemble import StackingClassifier, RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

X = sampled_data.drop(columns=['label'])
y = sampled_data['label']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Define base models
rf = RandomForestClassifier(n_estimators=100, random_state=42)
xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
svm = SVC(probability=True, random_state=42)

# Define meta-model
meta_model = LogisticRegression()

stack = StackingClassifier(
    estimators=[
        ('random_forest', rf),
        ('xgboost', xgb),
        ('svm', svm)
    ],
    final_estimator=meta_model,
    cv=5
)

# Train the stacking model
stack.fit(X_train, y_train)

# Make predictions
y_pred = stack.predict(X_test)

# Evaluate the performance
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy of Stacked Model: {accuracy:.2f}")