from flask import Flask, jsonify, render_template
from bitcoin import Bitcoin

app = Flask(__name__)
bitcoin = Bitcoin()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/bitcoin-info')
def bitcoin_info():
    bitcoin.fetch()  # Make sure this updates all your Bitcoin class data attributes
    return jsonify({
        "blockHeight": bitcoin.current_block_height(),
        "latestBlock": bitcoin.latestBlock,
        "peers": bitcoin.peers,
        "networkHashRate": bitcoin.networkHashRate,
        "mempoolInfo": bitcoin.mempoolInfo
    })

if __name__ == '__main__':
    app.run(debug=True)
