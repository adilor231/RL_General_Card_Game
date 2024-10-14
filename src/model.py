import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
import io

from constants import ALPHA

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, hidden2_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden2_size)
        self.linear3 = nn.Linear(hidden2_size, output_size)

    def forward(self, x):
        x = F.tanh(self.linear1(x))
        x = F.tanh(self.linear2(x))
        x = self.linear3(x)
        return x
    
    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)        
        torch.save(self.state_dict(), file_name)

    def load(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            return
        file_name = os.path.join(model_folder_path, file_name)
        if not os.path.exists(file_name):
            return
        self.load_state_dict(torch.load(file_name))  

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        #action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        if len(state.shape)==1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            #action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            #done = (done, )

        pred = self.model(state)
        target = pred.clone()
        
        if done: 
            Q_new = (1-ALPHA)*pred[0][action] + ALPHA*reward.item()
        if not done:
            Q_new = (1-ALPHA)*pred[0][action] + ALPHA*(reward.item() + self.gamma * torch.max(self.model(next_state[0])))
        target[0][action] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()