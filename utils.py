import numpy as np
import torch
import os, sys
import matplotlib.pyplot as plt
from custom import metrics, losses, models


def fullseed(seed=0xD153A53):
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)


def discretize_segmentation_maps(probs, threshold=0.5):
    threshold = torch.from_numpy(np.array(threshold)).to(probs.device)
    return probs > threshold


def get_metric(cfg):
    return getattr(sys.modules['custom.metrics'], cfg.metric)


def get_lossfn(cfg):
    return getattr(sys.modules['custom.losses'], cfg.loss_fn)


def get_model(cfg):
    if cfg.model == 'DeepLabV3':
        model = getattr(sys.modules['custom.models'], cfg.model)(in_channels=cfg.deeplab_inchannels,
                                                                 resnet=cfg.deeplab_backbone)

    return model


def get_optimizer(cfg):
    return


def get_scheduler(cfg):
    return


def get_paths(cfg):
    paths_folder = os.path.join(cfg.root_folder, cfg.data_folder, cfg.dataset_name)
    paths = np.array([os.path.join(paths_folder, x) for x in os.listdir(paths_folder)])
    return paths


def show_segmentation(model, loader, n=1, size=16, threshold=0.5, device=None):
    if not device:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Image, Prediction, Binarized prediction, True mask')
    k = 0
    for X, y in loader:
        with torch.no_grad():
            X = X.to(device)
            y = y.to(device)

            output = model(X)

            for i in range(len(X)):
                if len(torch.unique(y[i])) == 1:
                    continue
                plt.subplots(1, 8, figsize=(size, size))
                plt.subplot(1, 4, 1)
                plt.axis('off')
                plt.imshow(X[i].cpu().squeeze(), cmap='gray')
                plt.subplot(1, 4, 2)
                plt.axis('off')
                plt.imshow(output[i].cpu().squeeze(), cmap='gray')
                plt.subplot(1, 4, 3)
                plt.axis('off')
                plt.imshow(discretize_segmentation_maps(output[i].cpu().squeeze(), threshold=threshold), cmap='gray')
                plt.subplot(1, 4, 4)
                plt.axis('off')
                plt.imshow(y[i].cpu().squeeze(), cmap='gray')
                plt.show()
                k += 1
                if k == n:
                    return
