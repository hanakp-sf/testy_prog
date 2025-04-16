import matplotlib.pyplot as plt


plt.style.use('dark_background')

# Create a figure and axis
fig, ax = plt.subplots()
#ax.grid(True, which='both')

#spines su zobrazene osi, pravu a hornu vypnem, lavu a spodnu presuniem do stredu
ax.spines['left'].set_position('center')
ax.spines['right'].set_color('none')
ax.spines['bottom'].set_position('center')
ax.spines['top'].set_color('none')

# uplne vypnutie osi
#ax.set_axis_off()

mx = 15
for i in range(1,mx):
    ax.plot([-mx+i, 0], [0, i],'r')
    ax.plot([0, mx-i], [i, 0],'r')
    ax.plot([ mx-i, 0], [0, -i],'r')
    ax.plot([0, -i], [-mx+i, 0],'r')

# Set axis limits and show the plot
ax.set_xlim(-mx, mx)
ax.set_ylim(-mx, mx)
plt.axis('equal')  # To ensure the aspect ratio is maintained
plt.show()