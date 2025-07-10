# import matplotlib.pyplot as plt
# import json

# # Your data
# with open("./data.json", "r") as f:
#     data = json.load(f)

# for warpig, matches in data.items():
#     count = 0
#     total = 0
#     for date, length in matches.items():
#         count += 1
#         total += length
#         matches[date] = [length / 3600, (total / count) / 3600]

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
import numpy as np
# import mplcursors

# Load data
with open("./data.json", "r") as f:
    data = json.load(f)

num_warpigs = len(data)

# Set up overall figure and grid spec
fig = plt.figure(figsize=(14, 5 * num_warpigs))  # wider for chart + table
gs = gridspec.GridSpec(num_warpigs, 2, width_ratios=[3, 1])  # chart 3x wider than table

axes = []
for i in range(num_warpigs):
    ax = fig.add_subplot(gs[i, 0])  # Left plot
    axes.append(ax)

# Process each warpig
for i, (warpig, matches) in enumerate(data.items()):
    ax = axes[i]

    # Sort matches by date
    sorted_items = sorted(matches.items())
    durations = []
    averages = []

    total = 0
    for j, (date, length) in enumerate(sorted_items):
        hours = length / 3600
        total += hours
        avg = total / (j + 1)

        durations.append(hours)
        averages.append(avg)

    match_numbers = list(range(1, len(durations) + 1))

    # Plot duration and average
    line1, = ax.plot(match_numbers, durations, label='Match Duration (hrs)')
    line2, = ax.plot(match_numbers, averages, label='Running Avg (hrs)')
    ax.set_title(f"{warpig} - Match Durations")
    ax.set_ylabel("Hours")
    ax.grid(True)
    ax.legend()

    # Compute statistics
    durations_np = np.array(durations)
    stats_data = [
        ["Mean", f"{np.mean(durations_np):.2f} h"],
        ["Median", f"{np.median(durations_np):.2f} h"],
        ["Min", f"{np.min(durations_np):.2f} h"],
        ["Max", f"{np.max(durations_np):.2f} h"],
        ["Std Dev", f"{np.std(durations_np):.2f} h"]
    ]

    # Create table in right subplot
    table_ax = fig.add_subplot(gs[i, 1])  # Right table
    table_ax.axis('off')  # hide axis
    table = table_ax.table(cellText=stats_data,
                            colLabels=["Stat", "Value"],
                            loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)  # make rows taller

    # # Interactive hover
    # cursor = mplcursors.cursor([line1, line2], hover=True)
    # @cursor.connect("add")
    # def on_add(sel):
    #     index = int(sel.index)
    #     line_label = sel.artist.get_label()
    #     x = match_numbers[index]
    #     y = sel.artist.get_ydata()[index]
    #     sel.annotation.set(text=f"{line_label}\nMatch {x}\n{y:.2f} h")

axes[-1].set_xlabel("Match Number (ordered by date)")
plt.tight_layout()
plt.show()
