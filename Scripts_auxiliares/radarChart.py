import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns  # improves plot aesthetics


def _invert(x, limits):
    """inverts a value x on a scale from
    limits[0] to limits[1]"""
    return limits[1] - (x - limits[0])


def _scale_data(data, ranges):
    """scales data[1:] to ranges[0],
    inverts if the scale is reversed"""
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        assert (y1 <= d <= y2) or (y2 <= d <= y1)
    """
    for r in ranges:
        x1, x2 = r
        if x1 != x2:
            break """
    x1, x2 = ranges[0]
    d = data[0]
    if x1 > x2:
        d = _invert(d, (x1, x2))
        x1, x2 = x2, x1
    sdata = [d]
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        if y1 > y2:
            d = _invert(d, (y1, y2))
            y1, y2 = y2, y1
        sdata.append((d - y1) / (y2 - y1)
                     * (x2 - x1) + x1 if (y2 - y1) != 0 else d)
    return sdata


class ComplexRadar():
    def __init__(self, fig, variables, ranges,
                 n_ordinate_levels=6):
        angles = np.arange(0, 360, 360. / len(variables))

        axes = [fig.add_axes([0.05, 0.05, 0.9, 0.9], polar=True,
                             label="axes{}".format(i))
                for i in range(len(variables))]
        l, text = axes[0].set_thetagrids(angles,
                                         labels=variables,
                                         fontsize=14,
                                         rotation=angles[1],#-90,
                                         color='purple'
                                         )

        [txt.set_position((-0.05, -0.05)) for txt, angle in zip(text, angles)]
        [txt.set_rotation(angle - 90) for txt, angle in zip(text, angles)]
        for ax in axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)
        for i, ax in enumerate(axes):
            grid = np.linspace(*ranges[i],
                               num=n_ordinate_levels)
            gridlabel = ["{}".format(round(x, 2))
                         for x in grid]
            '''
            if ranges[i][0] > ranges[i][1]:
                grid = grid[::-1]  # hack to invert grid
                # gridlabels aren't reversed
            '''
            for gL in range(len(gridlabel)):
                if (gL != len(gridlabel)-1):
                    gridlabel[gL] = ""  # clean up origin
                else:
                    gridlabel[gL] = int(float(gridlabel[gL]))

            ax.set_rgrids(grid, labels=gridlabel,
                          angle=angles[i])
            ax.spines["polar"].set_visible(True)
            ax.set_ylim(*ranges[i])
        # variables for plotting
        self.angle = np.deg2rad(np.r_[angles, angles[0]])
        self.ranges = ranges
        self.ax = axes[0]

    def plot(self, data, legend, n_quintetos, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.plot(self.angle, np.r_[sdata, sdata[0]], label=legend, marker='o', ms=3, linewidth=1.5, alpha=0.5, *args, **kw)
        for an in range(len(data)):
            txt = str(data[an]) if type(data[an]) == "<class 'float'>" else str(round(data[an],1))
            self.ax.annotate(txt, xy = (self.angle[an], np.r_[sdata[an], sdata[0]][0]+sdata[0]*0.025), annotation_clip=True, *args, **kw )
        self.ax.legend(ncols=1, bbox_to_anchor=(0, 1.11 +0.05*n_quintetos),
              loc='upper left', fontsize='large')

    def fill(self, data, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.fill(self.angle, np.r_[sdata, sdata[0]], *args, **kw)


