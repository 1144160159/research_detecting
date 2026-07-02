from mpl_toolkits.axisartist.axislines import SubplotZero
import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure(1, (10, 6))

ax = SubplotZero(fig, 1, 1, 1)
fig.add_subplot(ax)

"""新建坐标轴"""
ax.axis["xzero"].set_visible(True)
ax.axis["xzero"].label.set_text("新建y=0坐标")
ax.axis["xzero"].label.set_color('green')
# ax.axis['yzero'].set_visible(True)
# ax.axis["yzero"].label.set_text("新建x=0坐标")

# 新建一条y=2横坐标轴
ax.axis["新建1"] = ax.new_floating_axis(nth_coord=0, value=2, axis_direction="bottom")
ax.axis["新建1"].toggle(all=True)
ax.axis["新建1"].label.set_text("y = 2横坐标")
ax.axis["新建1"].label.set_color('blue')

"""坐标箭头"""
ax.axis["xzero"].set_axisline_style("-|>")

"""隐藏坐标轴"""
# 方法一：隐藏上边及右边
# ax.axis["right"].set_visible(False)
# ax.axis["top"].set_visible(False)
# 方法二：可以一起写
ax.axis["top", 'right'].set_visible(False)
# 方法三：利用 for in
# for n in ["bottom", "top", "right"]:
#     ax.axis[n].set_visible(False)

"""设置刻度"""
ax.set_ylim(-3, 3)
ax.set_yticks([-1, -0.5, 0, 0.5, 1])
ax.set_xlim([-5, 8])
# ax.set_xticks([-5,5,1])

# 设置网格样式
ax.grid(True, linestyle='-.')

xx = np.arange(-4, 2 * np.pi, 0.01)
ax.plot(xx, np.sin(xx))

# 于 offset 处新建一条纵坐标
offset = (40, 0)
new_axisline = ax.get_grid_helper().new_fixed_axis
ax.axis["新建2"] = new_axisline(loc="right", offset=offset, axes=ax)
ax.axis["新建2"].label.set_text("新建纵坐标")
ax.axis["新建2"].label.set_color('red')

plt.show()
# 存为图像
# fig.savefig('test.png')