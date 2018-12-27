import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class DQN(nn.Module):

    def __init__(self):
        super(DQN, self).__init__()
        # self.conv1 = nn.Conv2d(3, 16, kernel_size=5, stride=2)
        # self.bn1 = nn.BatchNorm2d(16)
        # self.conv2 = nn.Conv2d(16, 32, kernel_size=5, stride=2)
        # self.bn2 = nn.BatchNorm2d(32)
        # self.conv3 = nn.Conv2d(32, 32, kernel_size=5, stride=2)
        # self.bn3 = nn.BatchNorm2d(32)
        self.dense_1 = nn.Linear(32*32*5 + 1, 256)
        self.dense_2 = nn.Linear(256, 128)
        self.dense_act = nn.Linear(128, 3)
        self.dense_arg = nn.Linear(128, 4)

    def forward(self, x):
        x = F.relu(self.dense_1(x))
        x = F.relu(self.dense_2(x))
        act = F.relu(self.dense_act(x))
        arg = F.relu(self.dense_arg(x))

        return act,arg