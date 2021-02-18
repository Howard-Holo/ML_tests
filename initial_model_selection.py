import pandas as pd
import time

_start_time = time.time()

def encode_str_label(_dataframe, _columnname):
    from sklearn.preprocessing import LabelEncoder
    _class_lb = LabelEncoder()
    _dataframe['%s' % _columnname] = _class_lb.fit_transform(_dataframe['%s' % _columnname].values)


def encode_str_labels(_dataframe, _labelList):
    from sklearn.preprocessing import LabelEncoder
    for _columnname in _labelList:
        _class_lb = LabelEncoder()
        _dataframe['%s' % _columnname] = _class_lb.fit_transform(_dataframe['%s' % _columnname].values)


train_set = pd.read_csv("train.csv")
test_set = pd.read_csv("test.csv")
N_train = train_set.shape[0]
N_test = test_set.shape[0]

all_set = pd.concat((train_set.iloc[:, 1:], test_set.iloc[:, 1:]))
str_set = all_set.dtypes[all_set.dtypes == 'object'].index
numeric_set = all_set.dtypes[all_set.dtypes != 'object'].index
all_set[numeric_set].apply(
    lambda x: ((x - x.mean()) / x.std())
)
encode_str_labels(all_set, str_set)
all_set = all_set.fillna(0)
train_set = all_set.iloc[:N_train]
test_set = all_set.iloc[N_train:, :-1]

print("Dataset cleared. Time at:", time.time() - _start_time)

_model_list = ["RF", "Linear", "SVM", "KNN", "DT", "AdaBoost", "GBRT", "Catboost", "ETR"]

init_result = []
for model_name in _model_list:
    for i in range(30):
        # initial judge between different models
        train_set_sample = train_set.sample(n=10000)
        X_train = train_set_sample.iloc[:, :-1]
        y_train = train_set_sample.iloc[:, -1]
        from sklearn.model_selection import train_test_split
        X_train, X_validation, y_train, y_validation = train_test_split(X_train, y_train, train_size=0.8)

        if model_name == "RF":
            from sklearn.ensemble import RandomForestRegressor
            model = RandomForestRegressor()
        elif model_name == "Linear":
            from sklearn import linear_model
            model = linear_model.LinearRegression()
        elif model_name == "SVM":
            from sklearn import svm
            model = svm.SVR()
        elif model_name == "KNN":
            from sklearn import neighbors
            model = neighbors.KNeighborsRegressor()
        elif model_name == "DT":
            from sklearn import tree
            model = tree.DecisionTreeRegressor()
        elif model_name == "AdaBoost":
            from sklearn.ensemble import AdaBoostRegressor
            model = AdaBoostRegressor()
        elif model_name == "GBRT":
            from sklearn.ensemble import GradientBoostingRegressor
            model = GradientBoostingRegressor()
        elif model_name == "Catboost":
            from catboost import CatBoostRegressor
            model = CatBoostRegressor()
        elif model_name == "ETR":
            from sklearn.tree import ExtraTreeRegressor
            model = ExtraTreeRegressor()

        model.fit(X_train, y_train)
        predict_val = model.predict(X_validation)

        # Model Performance
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        from math import sqrt
        RMSE = sqrt(mean_squared_error(y_validation, predict_val))
        # print("MSE:", mean_squared_error(y_validation, predict_val))
        # print("MAE:", mean_absolute_error(y_validation, predict_val))
        # print("R2:", r2_score(y_validation, predict_val))
        # print("RMSE:", sqrt(mean_squared_error(y_validation, predict_val)))

        init_result.append([model_name, RMSE])
        print("Model %s Round %f0 Finished. Time at:" % (model_name, i), time.time() - _start_time)

init_result = pd.DataFrame(init_result, columns=["Model", "RMSE"])
init_result.to_csv("init_result.csv")
print(init_result)