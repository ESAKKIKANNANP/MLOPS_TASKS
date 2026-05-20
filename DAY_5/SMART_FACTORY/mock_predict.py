import joblib
import pandas as pd

def predict_new_reading():
    # 1. Load the serialized model from disk
    model_filename = 'multivariable_model.joblib'
    print(f"Loading model from {model_filename}...")
    model = joblib.load(model_filename)
    
    # 2. Emulate a mock "new" machine reading
    # The features used were: 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Air temperature [K]'
    mock_data = {
        'Rotational speed [rpm]': [1520],
        'Torque [Nm]': [45.1],
        'Tool wear [min]': [12],
        'Air temperature [K]': [298.5]
    }
    mock_df = pd.DataFrame(mock_data)
    
    print("\nSimulating new machine reading:")
    print(mock_df)
    
    # 3. Predict the continuous target 'Process temperature [K]'
    prediction = model.predict(mock_df)
    
    print(f"\n=> Predicted Process Temperature: {prediction[0]:.2f} K")

if __name__ == "__main__":
    predict_new_reading()
