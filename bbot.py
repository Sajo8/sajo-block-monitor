import discord
import asyncio
import turtlecoin
import json
import time

#discord stuff
token = open('tokenfile').read()
client = discord.Client()

tc = turtlecoin.TurtleCoind(host='public.turtlenode.io', port=11898)

tclbh = tc.get_last_block_header()['result']

def getstats(height):

	tcgl = tc.get_last_block_header()['result']['block_header']

	#height of the latest block
	height = tcgl['height']
	#hash of latest block
	hash = tcgl['hash']
	# whether atest block is orphan or not
	orphan = tcgl['orphan_status']

	#reward of the latest block
	reward = tcgl['reward']
	#divide by 100 to convert into trtls from shells
	breward = reward / 100

	"""wheter the time the block took to make is acceptable or not"""

	timex = tcgl['timestamp'] #get the latest timestamp
	prevhash = tcgl['prev_hash']
	glb = tc.get_block(prevhash)['result']
	time2 = glb['block']['timestamp'] #use vars defined in past 2 lines to get timestamp of past block
	timed = timex - time2 #compare the difference between the two
	rock = "388916188715155467" #rock's discord user id
	pingrock = "<@" + rock + ">" #string which pings rock in discord
	blocktime = "" #set to nothing for now
	if timed <= 4:
		blocktime += f"Block was too fast, {timed} seconds"
		pingrock += "" #if time between blocks <4 seconds, mark it as too fast
	elif timed >= 90:
		blocktime += f'Took too long, {timed} seconds.'
		pingrock += "" #if time between blocks >90 secs, mark it as too fast
	else:
		blocktime += f"Took {timed} seconds to make, pretty nice"
		pingrock = "" #anywhere between 4-90 seconds for the block is alright

	#size of the block
	bsize = tc.get_block(hash)['result']
	bsizes = bsize['block']['blockSize']

	# number of transaction hashes in the block
	txs = tc.get_block(hash)['result']
	ntxs = len(txs['block']['transactions'])

	#each tx hash in the block
	hashes = [x['hash'] for x in txs['block']['transactions']]

	# size of each tx
	hahsizes = [z['size'] for z in txs['block']['transactions']]

	#size of all the txs
	txsize = txs['block']
	txsizes = txsize['transactionsCumulativeSize']


	for hash in hashes:
		#tx extra hash
		teta = tc.get_transaction(hash)['result']['tx']['extra']
		#Decoded version of tx_extra:
		try:
			deteta = bytes.fromhex(teta).decode('utf-8')
		except UnicodeDecodeError:
			deteta = "unable to decode, probably nothing in there"

	#size of tx extra
	txes =  bsizes-txsizes

	# % of txs in the block
	txp = txsizes/bsizes * 100

	# % of tx_extra in the block
	txep = txes/bsizes * 100

	return {'height': height, 'hash': hash, 'orphan': orphan, 'reward': breward, 'bsizes': bsizes, 'blocktime': blocktime, 'ntxs': ntxs, 'hashes': hashes, 'hahsizes': hahsizes, 'txsizes': txsizes, 'teta': teta, 'deteta': deteta, 'txes': txes, 'txp': txp, 'txep': txep, 'pingrock': pingrock}


def prettyPrintStats(blockstats):
	msg = "```WE FOUND A NEW BLOCK!\n"
	msg += f"\nHeight: {blockstats['height']} \n"
	msg += f"Hash: {blockstats['hash']} \n"
	msg += f"Orphan: {blockstats['orphan']} \n"
	msg += f"Reward: {blockstats['reward']} \n"
	msg += f"Size: {blockstats['bsizes']} \n"
	msg += f"Time took to make: {blockstats['blocktime']} \n"

	msg += f" \nNo. of txs in the block: {blockstats['ntxs']} \n"
	msg += f"Tx hashes in the block: {blockstats['hashes']} \n"
	msg += f"Size of each tx: {blockstats['hahsizes']} \n"
	msg += f"Size of all the txs: {blockstats['txsizes']} \n \n"

	msg += f"tx_extra hash: {blockstats['teta']} \n"
	msg += f"Decoded version of tx_extra: {blockstats['deteta']} \n"
	msg += f"Size of tx_extra: {blockstats['txes']} \n \n"

	msg += f"Percentage of txs in the block: {blockstats['txp']} % \n"
	msg += f"Percentage of tx_extra in the block: {blockstats['txep']} % ```"

	#msg += blockstats['pingrock']

	return msg
	print(msg)


@client.event
async def on_ready():
	print("connected")
	height = tclbh['block_header']['height'] #get the latest height
	while True:
		#prettyPrintStats(getstats(nheight))
		nheight = tc.get_block_count()['result']['count'] #get the latest height but in a while true loop
		if height != nheight:
			prettyPrintStats(getstats(nheight)) #updates the values stored in the vars which print out in discord

			await client.send_message(discord.Object(id='459931714471460864'), prettyPrintStats(getstats(nheight))) #send the message in discord
			print("val changed")
			print(nheight)
			print(height)
			height = nheight #set the height == latest height, so that it doesnt go cray cray after the first time the block changes
			print(height)
		await asyncio.sleep(0.5) #wait for a bit before it loops


client.run(token)
