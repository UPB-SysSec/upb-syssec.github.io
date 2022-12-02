import json

import matplotlib.pyplot as plt

FILETYPES = [
    # ".stl",
    ".scad",
    ".obj",
    ".step",
    ".stp",
    ".sldprt",
    ".skp",
    ".f3d",
    ".fcstd",
    ".dxf",
    # ".gcode",
    # ".ipt",
    # ".3mf",
    # ".blend",
    # ".123dx",
    # ".amf",
]


data = json.load(open("data/format_uploads_per_day_per_object.json"))
months = sorted(list(set(date[:-3] for date in data.keys())))
aggregated_data = {k: [0] * len(months) for k in FILETYPES}

for i, month in enumerate(months):
    for date in data:
        if date.startswith(month):
            for ft in FILETYPES:
                aggregated_data[ft][i] += data[date][ft]

# with open("data/format_uploads_per_month.csv", "w") as file:
#     for i, month in enumerate(months):
#         if i == 0:
#             file.write(f"index,month,{','.join(FILETYPES)}\n")

#         file.write(f"{i},{month},{','.join([str(aggregated_data[ft][i]) for ft in FILETYPES])}\n")
#     exit()

# with open("data/format_uploads_per_month-for-tex.txt", "w") as file:
#     for ft in FILETYPES:
#         file.write(f"\\addplot coordinates {{% {ft}\n")
#         for i, month in enumerate(months):
#             file.write(f"    ({month}-01,{aggregated_data[ft][i]})\n")
#         file.write("};\n")
#     exit()

fig, ax = plt.subplots()
for ft in FILETYPES:
    ax.plot(months, aggregated_data[ft], label=ft)

ax.set_xlabel("Months")
ax.set_ylabel("Number of Files")
# ax.set_title("Simple Plot")
ax.legend()
ax.set_yscale("log")
plt.xticks(rotation=90)
plt.show()
