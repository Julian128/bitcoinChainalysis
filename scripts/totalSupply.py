
subsidy = 5_000_000_000 # 50 BTC
subsidyInterval = 210000
totalSupply = 0
blockHeight = 1


while True:
    totalSupply += subsidy
    blockHeight += 1
    if blockHeight % subsidyInterval == 0:
        subsidy = subsidy >> 1

    if subsidy == 0:
        print(f'blockHeight: {blockHeight}, totalSupply: {totalSupply}')
        break