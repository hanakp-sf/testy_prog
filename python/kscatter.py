import matplotlib.pyplot as plt

# x-axis values
x = ['01','02','03','04','05','06','07','08','09','10', '01']

# y-axis values
y = ['12-01 01:00','12-01 01:30','12-01 01:00','12-01 01:00','12-01 05:45','12-01 01:00','12-01 01:00','12-01 01:00',
  '12-01 01:00','12-01 01:00','12-01 02:00']

clr = ['#ff0000'] * 10

clr.append('#00ff00')

# plotting points as a scatter plot
plt.scatter(x, y, label= "stars", c = clr, 
#color= "green", 
            marker= "s", s=60)

# x-axis label
plt.xlabel('x - axis')
# frequency label
plt.ylabel('time')
# plot title
plt.title('My scatter plot!')
# showing legend
plt.legend()

# function to show the plot
plt.show()