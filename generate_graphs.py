# Author: Andreas Petersen

# This script generates graphs from a CSV file containing transactions.

# CSV file has the following format:
# Date;Description;Amount;Balance;Currency;

# Example (top is latest transaction):
# 05-06-2020;Test;1,00;100,00;DKK;
# 04-06-2020;Test;1,00;99,00;DKK;
# 03-06-2020;Test;1,00;98,00;DKK;

# NOTE: There is no header or empty lines in the file.

import csv
import datetime
import glob
import os
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


def get_largest_transactions(
    amounts, descriptions, dates, amount_of_transactions_to_extract=3
):
    """Returns the n largest transactions"""
    # Get the indices of the largest transactions
    indices = np.argpartition(amounts, -amount_of_transactions_to_extract)[
        -amount_of_transactions_to_extract:
    ]

    # Get the largest transactions
    largest_transactions = [(amounts[i], descriptions[i], dates[i]) for i in indices]

    # Sort the transactions by amount
    largest_transactions.sort(key=lambda x: x[0], reverse=True)

    return np.copy(largest_transactions)


def generate_graphs(csv_file):
    """Generates graphs from the latest eksport file"""
    # Read CSV file. Encofing is UTF-8 with BOM
    with open(csv_file, "r", encoding="utf-8-sig") as csvfile:
        reader = csv.reader(csvfile, delimiter=";", quotechar='"')
        transactions = list(reader)

        # Get all dates
        dates = [datetime.datetime.strptime(row[0], "%d-%m-%Y") for row in transactions]

        # Get all amounts
        amounts = [
            float(row[2].replace(".", "").replace(",", ".")) for row in transactions
        ]

        # Get all balances
        balances = [
            float(row[3].replace(".", "").replace(",", ".")) for row in transactions
        ]

        # Get all descriptions
        descriptions = [row[1] for row in transactions]

        # Plot the data
        fig, ax = plt.subplots()
        ax.plot(dates, balances, "b-")

        # Set the x axis to be dates
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

        # Rotate the x axis labels
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment="right")

        # Set the y axis to be currency
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%d"))

        # Set the title
        ax.set_title("Balance")

        # Set the labels
        ax.set_xlabel("Date")
        ax.set_ylabel("Balance")

        # Convert dates to numbers
        converted_dates = mdates.date2num(dates)

        # Fit a line to the data
        polyfit = np.polyfit(converted_dates, balances, 1)
        polyfit_function = np.poly1d(polyfit)
        plt.plot(converted_dates, polyfit_function(converted_dates), "r--")

        # Add labels for the 3 largest transactions
        largest_transactions = get_largest_transactions(amounts, descriptions, dates)
        for transaction in largest_transactions:
            # Get the index of the transaction
            index = amounts.index(transaction[0])

            # Get the date of the transaction
            date = dates[index]

            # Get the balance of the transaction
            balance = balances[index]

            # Get the description of the transaction
            description = transaction[1]

            # Add the label
            plt.annotate(
                description,
                xy=(date, balance),
                xytext=(date, balance + 10),
                arrowprops=dict(facecolor="black", shrink=0.05),
            )

        # Show the grid
        ax.grid(True)
        # Show the plot in maximized window
        fig_manager = plt.get_current_fig_manager()
        fig_manager.window.showMaximized()
        # Show the plot
        plt.show()

        # Save the plot
        fig.savefig("balance.png")


if __name__ == "__main__":
    # Finds the latest eksport (*).csv file from the Downloads folder
    latest_file = max(
        glob.iglob(os.path.expanduser("~/Downloads/eksport*.csv")), key=os.path.getctime
    )
    # Check if the file exists
    if not os.path.isfile(latest_file):
        print("The file does not exist")
        sys.exit(1)

    # Generate the graphs
    generate_graphs(latest_file)
