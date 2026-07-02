import pandas as pd
import argparse
import numpy as np
import os


def generate_graph_seq2seq_io_data(
        df, x_offsets, y_offsets,scaler=None
):
    """
    Generate samples from
    :param df:
    :param x_offsets:
    :param y_offsets:
    :param add_time_in_day:True
    :param add_day_in_week:False
    :param scaler:
    :return:
    # x: (epoch_size, input_length, num_nodes, input_dim)
    # y: (epoch_size, output_length, num_nodes, output_dim)
    """

    num_samples, num_nodes = df.shape   #df.shape=(34272,207)
    df = df.values
    data = np.expand_dims(df[:,:-1], axis=-1)
    labels = np.expand_dims(df[:,-1], axis=-1)
    # data = np.expand_dims(df.values, axis=-1)  #data.shape=(34272,207,1),df.values是将df对象返回为numpy数组对象;[[...]...[...]],[[[]...[]]...[[]...[]]

    # epoch_len = num_samples + min(x_offsets) - max(y_offsets)
    x, y ,label= [], [],[]
    # t is the index of the last observation.
    min_t = abs(min(x_offsets))   #abs返回绝对值，min_t=11
    max_t = abs(num_samples - abs(max(y_offsets)))  # Exclusive,max_t=34272-12=34260
    for t in range(min_t, max_t):
        x_t = data[t + x_offsets, ...]
        y_t = data[t + y_offsets, ...]
        labels_t = labels[t + y_offsets, ...]
        labels_t = labels_t.reshape(12)
        x.append(x_t)
        y.append(y_t)
        label.append(labels_t)
    x = np.stack(x, axis=0)
    y = np.stack(y, axis=0)
    label = np.stack(label, axis=0)
    return x, y, label

def generate_train_val_test(args):
    # df = pd.read_csv(args.traffic_df_filename, sep=',',header=0,index_col=0)
    df_train = pd.read_csv(args.train_df_filename, sep=',',header=0,index_col=0)
    df_test = pd.read_csv(args.test_df_filename, sep=',',header=0,index_col=0)
    train = df_train 
    test = df_test 

    if 'timestamp' in train.columns:
        train = train.drop(columns=['timestamp'])
    if 'timestamp' in test.columns:
        test = test.drop(columns=['timestamp'])
    # if 'attack' in train.columns:
    #     train = train.drop(columns=['attack'])
    # if 'attack' in test.columns:
    #     test = test.drop(columns=['attack'])

    x_offsets = np.sort(
        # np.concatenate(([-week_size + 1, -day_size + 1], np.arange(-11, 1, 1)))
        np.concatenate((np.arange(-11, 1, 1),))
    )
    # Predict the next one hou  r
    y_offsets = np.sort(np.arange(1, 13, 1))
    # x: (num_samples, input_length, num_nodes, input_dim)
    # y: (num_samples, output_length, num_nodes, output_dim)
    x_train, y_train,train_label = generate_graph_seq2seq_io_data(
        train,
        x_offsets=x_offsets,
        y_offsets=y_offsets,
    )

    #test
    x_test, y_test,test_label = generate_graph_seq2seq_io_data(
        test,
        x_offsets=x_offsets,
        y_offsets=y_offsets,
    )
    print("x_train shape: ", x_train.shape, ", y_train shape: ", y_train.shape, ", train_label shape: ",train_label.shape) #x shape:  (34249, 12, 207, 2) , y shape:  (34249, 12, 207, 2)
    print("x_test shape: ", x_test.shape, ", y_test shape: ", y_test.shape, ", test_label shape: ", test_label.shape) #x shape:  (34249, 12, 207, 2) , y shape:  (34249, 12, 207, 2)

    # Write the data into npz file.
    # num_test = 6831, using the last 6831 examples as testing.
    # for the rest: 9/10 is used for training, and 1/10 is used for validation.
    num_train = round(x_train.shape[0] * 0.9)  #323974
    num_val = round(x_train.shape[0] - num_train)

    # train
    x_train, y_train,train_label = x_train[:num_train], y_train[:num_train],train_label[:num_train]
    # val
    x_val, y_val,val_label = x_train[-num_val:],y_train[-num_val:],train_label[-num_val:]

    for cat in ["train", "val", "test"]:
        _x, _y,_label = locals()["x_" + cat], locals()["y_" + cat], locals()[cat + "_label"]
        print(cat, "x: ", _x.shape, "y:", _y.shape)
        np.savez_compressed(
            args.output_dir + "/%s.npz" % cat,
            x=_x,
            y=_y,
            labels = _label,
            x_offsets=x_offsets.reshape(list(x_offsets.shape) + [1]),
            y_offsets=y_offsets.reshape(list(y_offsets.shape) + [1]),
        )

def main(args):
    print("Generating training data")
    generate_train_val_test(args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir", type=str, default="../data/smd", help="Output directory."
    )
    parser.add_argument(
        "--train_df_filename",
        type=str,
        default="../data/smd/train.csv",
        help="Raw traffic readings.",
    )
    parser.add_argument(
        "--test_df_filename",
        type=str,
        default="../data/smd/test.csv",
        help="Raw traffic readings.",
    )
    args = parser.parse_args()
    main(args)