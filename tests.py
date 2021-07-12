def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors)  # get length of colours list
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles

dismissed_handle = ax.plot(appeals[appeals['PAC_Decisi'] == 'Dismissed'].geometry.x,
                           appeals[appeals['PAC_Decisi'] == 'Dismissed'].geometry.y, 's', color='red', ms=4,
                           transform=myCRS)

appeal_outcomes = list(join.PAC_Decisi.unique())
appeal_outcomes.sort()

appeal_colours = ['lime', 'red', 'grey', 'orangered', 'tomato']

appeal_handles = generate_handles(join.PAC_Decisi.unique(), appeal_colours)

nice_appeals = []
for name in appeal_outcomes:
    nice_appeals.append(name.title())

handles = appeal_handles
labels = nice_appeals

leg = ax.legend(handles, labels, title='Enforcement Appeal Decisions', title_fontsize=10, fontsize=8, loc='upper left',
                frameon=True, framealpha=1)

def