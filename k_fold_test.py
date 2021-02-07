import numpy as np
import torch
import torch.nn as nn
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def encode_str_label(_dataframe, _columnname):
    from sklearn.preprocessing import LabelEncoder
    _class_lb = LabelEncoder()
    _dataframe['%s' % _columnname] = _class_lb.fit_transform(_dataframe['%s' % _columnname].values)


def encode_str_labels(_dataframe, _labelList):
    from sklearn.preprocessing import LabelEncoder
    for _columnname in _labelList:
        _class_lb = LabelEncoder()
        _dataframe['%s' % _columnname] = _class_lb.fit_transform(_dataframe['%s' % _columnname].values)


def normalize_cont(_dataframe, _columnname):
    _df_mean = _dataframe['%s' % _columnname].mean()
    _df_std = _dataframe['%s' % _columnname].std()
    _dataframe['%s' % _columnname].apply(
        lambda x: ((x - _df_mean) / _df_std)
    )


def normalize_conts(_dataframe, _labeList):
    for _columnname in _labeList:
        _df_mean = _dataframe['%s' % _columnname].mean()
        _df_std = _dataframe['%s' % _columnname].std()
        _dataframe['%s' % _columnname].apply(
            lambda x: ((x - _df_mean) / _df_std)
        )


"""
1. import data from csv files. And data display
"""
train_data = pd.read_csv("train.csv")
test_data = pd.read_csv("test.csv")

all_features = pd.concat((train_data.iloc[:, 1:-1], test_data.iloc[:, 1:-1]))
str_features = all_features.dtypes[all_features.dtypes == 'object'].index
numeric_features = all_features.dtypes[all_features.dtypes != 'object'].index
all_features[numeric_features].apply(
    lambda x: ((x - x.mean()) / x.std())
)
encode_str_labels(all_features, str_features)
all_features = all_features.fillna(0)

n_train = train_data.shape[0]
train_features = torch.tensor(all_features[:n_train].values, dtype=torch.float)
test_features = torch.tensor(all_features[n_train:].values, dtype=torch.float)
train_labels = torch.tensor(train_data.target.values, dtype=torch.float).view(-1, 1)

"""
2. Model Construction
"""

loss = torch.nn.MSELoss()


def get_net(feature_num):
    net = nn.Linear(feature_num, 1)
    for param in net.parameters():
        nn.init.normal_(param, mean=0, std=0.01)
    return net


def rmse(net, features, labels):
    with torch.no_grad():
        clipped_preds = torch.max(net(features), torch.tensor(1.0))
        rmse = torch.sqrt(2 * loss(clipped_preds, labels).mean())
    return rmse.item()


def train(net, train_features, train_labels, test_features, test_labels,
          num_epochs, learning_rate, weight_decay, batch_size):
    train_ls, test_ls = [], []
    dataset = torch.utils.data.TensorDataset(train_features, train_labels)
    train_iter = torch.utils.data.DataLoader(dataset, batch_size, shuffle=True)
    optimizer = torch.optim.Adam(params=net.parameters(),
                                 lr=learning_rate, weight_decay=weight_decay
                                 )
    net = net.float()

    for epoch in range(num_epochs):
        for X, y in train_iter:
            l = loss(net(X.float()), y.float())
            optimizer.zero_grad()
            l.backward()
            optimizer.step()
        train_ls.append(rmse(net, test_features, test_labels))
        if test_labels is not None:
            test_ls.append(rmse(net, test_features, test_labels))
    return train_ls, test_ls


def get_k_fold_data(k, i, X, y):
    assert k > 1
    fold_size = X.shape[0] // k
    X_train, y_train = None, None

    for j in range(k):
        idx = slice(j * fold_size, (j + 1) * fold_size)
        X_part, y_part = X[idx, :], y[idx]

        if i == j:
            X_valid, y_valid = X_part, y_part
        elif X_train is None:
            X_train, y_train = X_part, y_part
        else:
            X_train = torch.cat((X_train, X_part), dim=0)
            y_train = torch.cat((y_train, y_part), dim=0)
    return X_train, y_train, X_valid, y_valid


def k_fold(k, X_train, y_train, num_epochs,
           learning_rate, weight_decay, batch_size):
    train_l_sum, valid_l_sum = 0, 0
    for i in range(k):
        print("fold %d started." % i)

        data = get_k_fold_data(k, i, X_train, y_train)
        net = get_net(X_train.shape[1])
        train_ls, valid_ls = train(net, *data, num_epochs,
                                   learning_rate, weight_decay, batch_size
                                   )
        train_l_sum += train_ls[-1]
        valid_l_sum += valid_ls[-1]
        # if i == 0:
        #     d2l.semilogy(range(1, num_epochs + 1), train_ls, 'epochs', 'rmse',
        #                  range(1, num_epochs + 1), valid_ls, ['train', 'valid']
        #                  )
        print("fold %d, train rmse %f, valid rmse %f" % (i, train_ls[-1], valid_ls[-1]))

    return train_l_sum / k, valid_l_sum / k


k, num_epochs, lr, weight_decay, batch_size = 5, 100, 0.1, 0, 64

# print("Data Initialized. Ready to train.")
#
# train_l, valid_l = k_fold(k, train_features, train_labels,
#                           num_epochs, lr, weight_decay, batch_size
#                           )
# print("%d-fold validation: avg train rmse %f, avg valid rmse %f" % (k, train_l, valid_l))


def train_and_pred(train_features, test_features, train_labels, test_data,
                   num_epochs, lr, weight_decay, batch_size):
    net = get_net(train_features.shape[1])
    train_ls, _ = train(net, train_features, train_labels, None, None,
                        num_epochs, lr, weight_decay, batch_size)
    print("train rmse%f" % train_ls[-1])
    preds = net(test_features).detach().numpy()
    test_data['target'] = pd.Series(preds.reshape(1, -1)[0])
    submission = pd.concat([test_data['id'], test_data['target']], axis=1)
    submission.to_csv("submission.csv", index=False)

train_and_pred(train_features, test_features, train_labels, test_data,
               num_epochs, lr, weight_decay, batch_size)
