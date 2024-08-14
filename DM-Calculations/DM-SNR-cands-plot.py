#%% 
import matplotlib.pyplot as plt
import scienceplots; plt.style.use('science')
import numpy as np
import pandas as pd 

df = pd.read_csv('cand_list.csv')
print(df.head())
# %%

# mask non float values
plt.figure(figsize=(4,4), dpi=200)
df = df.apply(pd.to_numeric, errors='coerce')
plt.scatter(df['dm'], df['sigma'], s = 1, c = 'k')
plt.xlabel('DM [pc cm$^{-3}$]')
plt.ylabel('$\sigma$')

plt.figure(figsize=(4,4), dpi=200)
df = df.apply(pd.to_numeric, errors='coerce')
plt.scatter(df['f'], df['sigma'], s = 1, c = 'k')
plt.xscale('log')
# plt.yscale('log')
plt.xlabel('Spin Frequency [Hz]')
plt.ylabel('$\sigma$')

# import plotly.graph_objects as go

# x = df['dm']; y = df['sigma']; z = df['f']

# # Create a 3D scatter plot
# fig = go.Figure(data=[go.Scatter3d(
#     x=x,
#     y=y,
#     z=z,
#     mode='markers',
#     marker=dict(
#         size=6,
#         color=z,                # set color to an array/list of desired values
#         colorscale='Viridis',    # choose a colorscale
#         opacity=0.8
#     )
# )])

# # Set the title and axis labels
# fig.update_layout(scene = dict(
#                     xaxis_title='DM [pc cm$^{-3}$]',
#                     yaxis_title='$\sigma$',
#                     zaxis_title='Frequency [MHz]'),
#                   width=700,
#                   margin=dict(r=20, b=10, l=10, t=10))

# fig.show()