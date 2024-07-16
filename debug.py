import matplotlib.pyplot as plt
from IPython import display
import pandas as pd

plt.ion()

def plot_moving(series, lag):
    n = len(series)
    data = {
        'index': pd.Series(range(n)),
        'value': pd.Series(range(n)).apply(lambda x: series[x])
    }
    df = pd.DataFrame(data)
    df['moving_average'] = df['value'].rolling(window=lag).mean()
    plt.figure(figsize=(10, 6))
    plt.plot(df['index'], df['value'], label='Wins')
    plt.plot(df['index'], df['moving_average'], label='Moving Average', color='orange')
    plt.xlabel('Index')
    plt.ylabel('Wins')
    plt.title('Moving Average Plot')
    plt.legend()
    plt.show(block=True)
    plt.savefig("winning_plot.png")

def plot(*args):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title("Training...")
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    for i, score in enumerate(args):
        color = ""
        if i == 0: color="Blue"
        if i == 1: color="Red"
        if i == 2: color="Green"
        if i == 3: color="Yellow"
        plt.plot(score, color=color)
    plt.ylim(ymin=0)
    for score in args:
        plt.text(len(score)-1, score[-1], str(score[-1]))
    plt.show(block=False)
    plt.pause(.005)   

class DebugItem:
    def __init__(self, string, time):
        self.item = string
        self.time = time