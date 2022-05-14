from get_data import get_train_data
from preprocessing import prep
from train import train


if __name__ == '__main__':

    get_train_data()
    prep()
    train()
