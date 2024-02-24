from app.clients.StockClient import StockClient


def main():
    stocks = StockClient.getStocks()

    print(stocks)


if __name__ == "__main__":
    main()
