import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from datetime import datetime, timedelta
from sklearn.metrics import accuracy_score
import pickle
from sklearn.pipeline import Pipeline


def train():
    date_s = datetime.now().date()
    path = f'prep_data/model_data{date_s}.csv'
    df = pd.read_csv(path)


    print(df.info())

    # Prepering the data
    X = df.drop(columns = 'result')
    y = df['result']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=12)

    sc_x = StandardScaler()


    model = Pipeline([
        ('scale', StandardScaler()),
        ('clf', LogisticRegression())])

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acu_socre = accuracy_score(y_test,y_pred)

    pickle.dump(0.1,open('pickeld_models/old_model_acu.sav', 'wb'))
    # save model and accuracuy score
    old_score = pickle.load(open('pickeld_models/old_model_acu.sav', 'rb'))

    if acu_socre > old_score:
        pickle.dump(acu_socre, open('pickeld_models/old_model_acu.sav', 'wb'))
        pickle.dump(model, open(f'pickeld_models/model{date_s}.sav', 'wb'))
    else:
        date_y = datetime.now() - timedelta(days = 1)
        date_y = date_y.date()
        old_model = pickle.load(open(f'pickeld_models/model{date_y}.sav', 'rb'))








