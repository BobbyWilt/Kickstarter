# -*- coding: utf-8 -*-
"""FT-KickStarter-05.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YNL0u2KB0FZlkby34XnC6fqkW7DKhN4r
"""

!pip install scikit-learn==0.24.1

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight

import tensorflow as tf

data = pd.read_csv('https://raw.githubusercontent.com/FT-Kickstarter-05/Kickstarter/main/2018_ks_data.csv')

data.head()

data.info()

"""# Cleaning and preprocessing """

unneeded_columns = ['ID', 'name']
data = data.drop(unneeded_columns, axis=1)

data.head()

data.isna().sum()

data['usd pledged'].mean()

data['usd pledged'] = data['usd pledged'].fillna(data['usd pledged'].mean())

data.isna().sum()

data.isna().sum().sum()

data['state'].unique()

data.query("state != 'failed' and state != 'successful'")

data.shape

data.query("state != 'failed' and state != 'successful'").index

data = data.drop(data.query("state != 'failed' and state != 'successful'").index, axis=0).reset_index(drop=True)

print(data.shape)
data.head()

data['state'].unique()

"""# Feature Engineering and Encoding

### Change Date to month and year and delete date
### For deadline and launched dates
"""

data.head()

data['deadline'].apply(lambda x: x[0:4])

data['deadline'].apply(lambda x: x[5:7])

data['deadline_year'] = data['deadline'].apply(lambda x: np.float(x[0:4]))
data['deadline_month'] = data['deadline'].apply(lambda x: np.float(x[5:7]))

data['launched_year'] = data['launched'].apply(lambda x: np.float(x[0:4]))
data['launched_month'] = data['launched'].apply(lambda x: np.float(x[5:7]))

data = data.drop(['deadline', 'launched'], axis=1)

"""### Binary encode 'state' column"""

data['state'].apply(lambda x: 1 if x == 'successful' else 0)

data['state'] = data['state'].apply(lambda x: 1 if x == 'successful' else 0)

data.head()

"""### OneHotEncode 'category','main_category'
### 'currency'	, 'country'
"""

from sys import prefix
def onehot_encode(df, columns, prefixes):
  df = df.copy()
  for column, prefix in zip(columns, prefixes):
    dummies = pd.get_dummies(df[column], prefix=prefix)
    df = pd.concat([df, dummies], axis=1)
    df = df.drop(column, axis=1)
  return df

data = onehot_encode(
    data,
    ['category', 'main_category', 'currency', 'country'],
    ['cat', 'main_cat', 'curr', 'country']
)

print(data.shape)
data.head()

"""# Our Data is fully numeric
### We are ready to split and scale the data
"""

y = data.loc[:, 'state']
X = data.drop('state', axis=1)

"""### We only want to scale X, we don’t want to scale what we are trying to predict."""

scaler = StandardScaler()
X = scaler.fit_transform(X)

"""### Each column has a mean of 0, and a variance of 1"""

pd.DataFrame(X)

"""### Split Data"""

X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, random_state=34)

"""### Modeling and Training"""

X.shape

y.shape

"""### How skewed our our classes"""

y.mean()

"""### 40% positive and 60% negative

### We will use class_weight from SKLearn
### It allows us to generate weights for all the imbalanced classes
"""

y_train.unique()

# This will compute class weights on y_train for classes in y_train.unique()
# with a mode of balanced.
class_weights = class_weight.compute_class_weight(
                                        "balanced",
                                        y_train.unique(),
                                        y_train                                                    
                                    )
class_weights = dict(enumerate(class_weights))
class_weights

inputs = tf.keras.Input(shape=(221,))
x = tf.keras.layers.Dense(64, activation='relu')(inputs)
x = tf.keras.layers.Dense(64, activation='relu')(x)
outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)

model = tf.keras.Model(inputs, outputs)


model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=[
        'accuracy',
        tf.keras.metrics.AUC(name='auc') # Area Under the Curve of the (ROC)Receiver Operating Curve
    ]
)
batch_size = 64
epochs = 100 # We are using a large amount of epochs because we are using early stopping

history = model.fit(
    X_train,
    y_train,
    validation_split=0.2,
    class_weight=class_weights, # This will assighn weights to the two classes 
    #to penalize the out of balance 
    batch_size=batch_size,
    epochs=epochs,
    callbacks=[
        tf.keras.callbacks.EarlyStopping( # This is a great callback that lets us monitor a metric or loss value
            monitor='val_loss',
            patience=3,
            restore_best_weights=True,
            verbose=1
        )
    ],
    verbose=2
)

"""# Results"""

model.evaluate(X_test, y_test)
