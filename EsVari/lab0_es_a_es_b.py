import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

table = pd.read_csv("sales_data.csv")
totalProfit = table["total_profit"]

figure1, ax1 = plt.subplots()
ax1.plot(totalProfit, color='r', marker='o', markerfacecolor='k', linestyle='-', linewidth=3)
ax1.set_title("Profit data of last year")

figure2, ax2 = plt.subplots()
ax2.plot(table["facecream"], label="Facecream")
ax2.plot(table["facewash"], label="Facewash")
ax2.plot(table["toothpaste"], label="Toothpaste")
ax2.plot(table["bathingsoap"], label="Bathingsoap")
ax2.plot(table["shampoo"], label="Shampoo")
ax2.plot(table["moisturizer"], label="Moisturizer")
ax2.legend()

figure3, ax3 = plt.subplots()
ax3.scatter(table["month_number"],table["toothpaste"])

figure4, ax4 = plt.subplots()
ax4.bar(table["month_number"], table["bathingsoap"])

figure5, ax5 = plt.subplots()
ax5.hist(totalProfit)

plt.show()