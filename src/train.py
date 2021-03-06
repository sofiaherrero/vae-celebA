from vae import VAE
from dataset import Dataset

from datetime import datetime as dt
from keras.callbacks import ModelCheckpoint, TensorBoard
import os
import pytz
import yaml

os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"


def train():
    with open("config.yml", 'r') as ymlfile:
        params = yaml.safe_load(ymlfile)

    dataset = Dataset(train_file='../data/Eval/train.csv',
                      val_file='../data/Eval/val.csv',
                      test_file='../data/Eval/test.csv',
                      images_path='../data/Img/',
                      image_target_size=params['image_shape'])

    train_generator = dataset.get_train_generator(params['batch_size'], params['seed'])
    val_generator = dataset.get_val_generator(params['batch_size'], params['seed'])

    vae = VAE(params['image_shape'], params['latent_dim'])

    log_dir = append_datetime_to_path()
    callbacks_list = [
        ModelCheckpoint(filepath=os.path.join(log_dir, 'vae_weights.h5'), monitor='val_loss', save_best_only=True,
                        save_weights_only=True),
        TensorBoard(log_dir=log_dir, write_graph=True)]

    history = vae.model.fit_generator(
        train_generator,
        steps_per_epoch=len(train_generator),
        epochs=params['epochs'],
        callbacks=callbacks_list,
        validation_data=val_generator,
        validation_steps=len(val_generator))

    # TODO: run test
    return history


def append_datetime_to_path():
    pst = pytz.timezone('Europe/Amsterdam')
    now = dt.strftime(dt.now().astimezone(pst), "%Y-%m-%d-%H%M%S")
    log_base_dir = '../logs'
    log_dir = os.path.join(log_base_dir, f'model-{now}')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


if __name__ == "__main__":
    train()
