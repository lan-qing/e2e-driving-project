import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import transforms
from tqdm import tqdm
import pandas as pd
from PIL import Image

class PilotNet(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv1 = nn.Conv2d(3, 24, 5, stride=2)
        self.conv2 = nn.Conv2d(24, 36, 5, stride=2)
        self.conv3 = nn.Conv2d(36, 48, 5, stride=2)
        self.conv4 = nn.Conv2d(48, 64, 3)
        self.conv5 = nn.Conv2d(64, 64, 3)
        self.nn6 = nn.Linear(1152, 100)
        self.nn7 = nn.Linear(100, 50)
        self.nn8 = nn.Linear(50, 10)
        self.nn9 = nn.Linear(10, 2) # throttle, steer

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x)) 
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = F.relu(self.conv5(x))
        x = x.view(x.size(0), -1)
        x = F.relu(self.nn6(x))
        x = F.relu(self.nn7(x))
        x = F.relu(self.nn8(x))
        x = self.nn9(x)

        return x
    
   
if __name__ == "__main__":
    from utils import Data
    data = Data()

    train_x, train_y, val_x, val_y = data.get_tensors()

    model = PilotNet()
    model.train()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.MSELoss()

    losses = []
    for epoch in tqdm(range(20), desc="Epoch"):
        for i in tqdm(range(len(train_x)), desc="Train", leave=False):
            optimizer.zero_grad()
            out = model(train_x[i].unsqueeze(0))
            loss = criterion(out, train_y[i].unsqueeze(0))
            loss.backward()
            optimizer.step()

        with torch.no_grad():
            for i in tqdm(range(len(val_x)), desc="Val", leave=False):
                out = model(val_x[i].unsqueeze(0))
                loss = criterion(out, val_y[i].unsqueeze(0))
                losses.append(loss.item())

        print(f"Epoch {epoch}, Loss: {loss.item()}")

    torch.save(model.state_dict(), "model.pth")

    # plot losses
    pd.Series(losses).plot()
