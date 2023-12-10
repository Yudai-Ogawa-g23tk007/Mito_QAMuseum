import matplotlib.pyplot as plt
from io import BytesIO
import base64
from PIL import Image

def AllViewSpot():
    x=[

    ]
    
    y=[

    ]
    
    return x,y

def Select_map(now_spot):
    map_img = {i: f"media/map_{i}.png" for i in range(1, 20)}
    if now_spot in map_img:
        img = map_img[now_spot]
    return img

def plot_graph(now_spot,next_spot,path):
    graph=0
    return graph

"""
def Output_graph():
    buffer = BytesIO()
    plt.savefig(buffer,format="png",transparent=True)
    buffer.seek(0)
    img = buffer.getvalue()
    graph = base64.b64encode(img)
    graph = graph.decode("utf-8")
    buffer.close()
    return graph
"""
def Next_imgae(next_spot):
    next_img={i: f"media/media/omura_{i}.png" for i in range(0, 19)}
    if next_spot in next_img:
        img = next_img[next_spot]
    return img