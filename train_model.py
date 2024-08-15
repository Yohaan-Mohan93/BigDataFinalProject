import joblib
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer

# Load the JSON files
with open('AllIdentifiers.json', 'r', encoding='utf-8') as f:
    identifiers_data = json.load(f)['data']

with open('AllPrices.json', 'r', encoding='utf-8') as f:
    prices_data = json.load(f)['data']

# Convert the JSON data to DataFrames
identifiers_df = pd.DataFrame.from_dict(identifiers_data, orient='index')
prices_df = pd.DataFrame.from_dict(prices_data, orient='index')

# Extract the TCGPlayer prices from the prices DataFrame
def extract_tcgplayer_prices(row):
    if isinstance(row.get('paper'), dict):
        tcgplayer_data = row['paper'].get('tcgplayer')
        if isinstance(tcgplayer_data, dict):
            retail_data = tcgplayer_data.get('retail')
            if isinstance(retail_data, dict):
                normal_prices = retail_data.get('normal')
                if isinstance(normal_prices, dict):
                    return pd.Series(normal_prices)
    return pd.Series(dtype=np.float64)

# Apply the function to extract TCGPlayer prices
tcgplayer_prices_df = prices_df.apply(lambda row: extract_tcgplayer_prices(row), axis=1)

# Merge the two DataFrames on the index (which is the UUID)
merged_df = identifiers_df.join(tcgplayer_prices_df)

# Check if merged_df is empty
if merged_df.empty:
    raise ValueError("No data available after merging. Please check the extraction logic.")

# Keep the card name and set for later lookup
X = merged_df.drop(columns=['artist', 'uuid'])  # Retain name and setCode
y = merged_df.iloc[:, -1]  # Assume the last column is the target price

# Drop any rows with missing target values
X.dropna(subset=[y.name], inplace=True)
y = y[X.index]

# Ensure only numeric data is being used
X_numeric = X.select_dtypes(include=[np.number])

# Check for missing values in the dataset
missing_values = X_numeric.isna().sum()
print("Missing values in each column of X_numeric:")
print(missing_values[missing_values > 0])

# Impute missing values with the median
imputer = SimpleImputer(strategy='median')
X_numeric_imputed = imputer.fit_transform(X_numeric)

# Debugging print statements
print(f"Shape of X_numeric after imputation: {X_numeric_imputed.shape}")
print(f"Sample of X_numeric after imputation: {X_numeric_imputed[:5]}")

# Check if X_numeric_imputed and y are empty
if X_numeric_imputed.shape[0] == 0 or y.shape[0] == 0:
    raise ValueError("No data available after handling missing values. Please check the data.")

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_numeric_imputed, y, test_size=0.2, random_state=42)

# Train a simple model (e.g., linear regression)
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)

print(f"Mean Squared Error: {mse}")

# Save the model for future use
joblib.dump(model, 'card_price_models.pkl')

print("Training complete. Model saved to 'card_price_models.pkl'.")
