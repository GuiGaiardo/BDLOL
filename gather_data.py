#Author: Guilherme Gaiardo - UFSM - 04/2016

from collections import Counter as c
import json
import requests
import time
import sys
from raw_to_csv import *

if len(sys.argv) != 5:
	print("Usage: python3 gather_data.py <training file name> <test file name> <unknown samples file name> <n_train>")
	exit()



class Requester:
	def __init__(self, API_KEY):
		self.t_ini = time.time()
		self.n_requests = 1
		self.n_failed = 0
		self.API_KEY = API_KEY

	#makes the request, if possible, and returns the json object
	def make_request(self, url):
		elapsed_time = time.time() - self.t_ini

		if self.n_requests%10 == 0:
			time_to_wait = 10.5 - elapsed_time
			if time_to_wait > 0:
				time.sleep(time_to_wait)
		
		if elapsed_time >= 10.5:
			self.n_requests = 0

		while True:
			request = requests.get(url + self.API_KEY)

			if request.status_code == 200:
				self.n_failed = 0
				break
			self.n_failed += 1
			print("N fails:  " + str(self.n_failed))
			if self.n_failed > 5:
				print("Too many errors!\nExiting!")
				break
			time.sleep(2)

		if self.n_requests == 0:
			self.t_ini = time.time()
		self.n_requests += 1

		if request.status_code != 200:
			self._show_error_msg(url, request.json())
			exit()

		return request.json()


	#simply shows an error message if something went wrong with the API
	def _show_error_msg(self, url, error):
		print("\n\n#####################")
		print("URL: " + url)
		print("Error " + str(error['status']['status_code']))
		print(error['status']['message'])





#Function to retrieve a list with summoners id
#of all players in master and challenger tier of the listed regions
def get_summoners_list(n):
	regions = ["BR", "NA", "EUNE", "EUW", "JP", "KR", "LAN", "LAS", "OCE", "TR", "RU"]
	game_type = "RANKED_SOLO_5x5"
	tiers = ["challenger", "master"]

	summoners_id_list = {'BR':[], 'NA':[], "EUNE":[], "EUW":[], "JP":[], "KR":[], "LAN":[], "LAS":[], "OCE":[], "TR":[], "RU":[]}

	for region in regions:
		count = 0
		for tier in tiers:
			if count == n:
				break

			if (region == "JP" and tier == "master"):
				continue
			url = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v2.5/league/" + tier + "?type=" + game_type + "&api_key="
			data = requester.make_request(url)			

			summoners = data['entries']

			for summoner in summoners:
				count += 1
				print(">"+region+"  "+summoner['playerOrTeamId'])
				summoners_id_list[region].append(summoner['playerOrTeamId'])
				if count == n:
					break

	return summoners_id_list



#get ranked summoners data and also its supposed main role in the game
def get_ranked_data(summoners_id_list):
	regions = ["BR", "NA", "EUNE", "EUW", "JP", "KR", "LAN", "LAS", "OCE", "TR", "RU"]
	#regions = ["br"]

	raw_data = {}

	n_summoners = 0
	for reg in regions:
		n_summoners += len(summoners_id_list[reg])
	#n_summoners = len(summoners_id_list['br'])
	counter = 1

	for region in regions:
		for summoner_id in summoners_id_list[region]:
			url = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v1.3/stats/by-summoner/" + summoner_id + "/ranked?season=SEASON2017&api_key="
			summoner_data = requester.make_request(url)
			print("\n\n" + str(counter) + "/" + str(n_summoners) + " requests left.")
			counter += 1
			
			#supposed summoners role
			role = assert_summoner_role(summoner_id, region)

			#actually useful data -> {summoner_id : (role, [player_aggregated_data])}
			raw_data[summoner_id] = (role, get_useful_data(summoner_data))

	return raw_data




#gather the useful data over all the summoners data
def get_useful_data(summoner_data):
	attributes = []
	for champ in summoner_data['champions']:
		if champ['id'] == 0:
			champ_data = champ['stats']

			total_sessions = champ_data["totalSessionsPlayed"]
			
			#wanted statistics
			attributes.append(champ_data["totalSessionsPlayed"])
			attributes.append(champ_data["totalChampionKills"])
			attributes.append(champ_data["totalDeathsPerSession"])
			attributes.append(champ_data["totalAssists"])
			attributes.append(champ_data["totalMinionKills"])
			attributes.append(champ_data["totalNeutralMinionsKilled"])
			attributes.append(champ_data["totalDamageDealt"])
			attributes.append(champ_data["totalDamageTaken"])
			attributes.append(champ_data["totalGoldEarned"])
			attributes.append(champ_data["totalHeal"])
			attributes.append(champ_data["totalMagicDamageDealt"])
			attributes.append(champ_data["totalPhysicalDamageDealt"])
			attributes.append(champ_data["totalDoubleKills"])
			attributes.append(champ_data["totalFirstBlood"])
			attributes.append(champ_data["totalPentaKills"])
			attributes.append(champ_data["totalQuadraKills"])
			attributes.append(champ_data["totalTripleKills"])
			attributes.append(champ_data["totalTurretsKilled"])
			attributes.append(champ_data["totalUnrealKills"])
			# attributes.append(champ_data["totalChampionKills"]/total_sessions)
			# attributes.append(champ_data["totalDeathsPerSession"]/total_sessions)
			# attributes.append(champ_data["totalAssists"]/total_sessions)
			# attributes.append(champ_data["totalMinionKills"]/total_sessions)
			# attributes.append(champ_data["totalNeutralMinionsKilled"]/total_sessions)
			# attributes.append(champ_data["totalDamageDealt"]/total_sessions)
			# attributes.append(champ_data["totalDamageTaken"]/total_sessions)
			# attributes.append(champ_data["totalGoldEarned"]/total_sessions)
			# attributes.append(champ_data["totalHeal"]/total_sessions)
			# attributes.append(champ_data["totalMagicDamageDealt"]/total_sessions)
			# attributes.append(champ_data["totalPhysicalDamageDealt"]/total_sessions)
			# attributes.append(champ_data["totalDoubleKills"]/total_sessions)
			# attributes.append(champ_data["totalFirstBlood"]/total_sessions)
			# attributes.append(champ_data["totalPentaKills"]/total_sessions)
			# attributes.append(champ_data["totalQuadraKills"]/total_sessions)
			# attributes.append(champ_data["totalTripleKills"]/total_sessions)
			# attributes.append(champ_data["totalTurretsKilled"]/total_sessions)
			# attributes.append(champ_data["totalUnrealKills"]/total_sessions)
			attributes.append(champ_data["maxChampionsKilled"])
			attributes.append(champ_data["maxLargestCriticalStrike"])
			attributes.append(champ_data["maxLargestKillingSpree"])
			break

	return attributes



#Returns the most played role from a match list
def get_role(match_list):
	lanes = []
	roles = []
	for match in match_list:
		lanes.append(match["lane"])
		roles.append(match["role"])

	lane_counter = c(lanes).most_common()[0][0]
	role_counter = c(roles).most_common()[0][0]

	if lane_counter == "MID" or lane_counter == "MIDDLE":
		role = "MID"
	elif lane_counter == "JUNGLE":
		role = "JUNGLE"
	elif lane_counter == "TOP":
		role = "TOP"
	elif role_counter == "DUO_CARRY":
		role = "ADC"
	elif role_counter == "DUO_SUPPORT":
		role = "SUPPORT"
	else:
		role = "UNKNOWN"
		print(lane_counter)
		print(role_counter)

	return role




def assert_summoner_role(summoner_id, region):
	url = "https://" + str(region) + ".api.pvp.net/api/lol/" + str(region) + "/v2.2/matchlist/by-summoner/" + str (summoner_id) + "?beginTime=1481108400000&api_key="
	match_list = requester.make_request(url)
	return get_role(match_list["matches"])



###########################################################
#					SCRIPT IN ACTION!					  #
###########################################################



#API_KEY = sys.argv[1]
API_KEY = "690c2fbb-ed65-4054-a0c3-4eb6325e21e5"
train_file_name = sys.argv[1]
test_file_name = sys.argv[2]
unknown_file_name = sys.argv[3]
n_train = int(sys.argv[4])
requester = Requester(API_KEY)

summoners_id_list = get_summoners_list(n_train)

raw_data = get_ranked_data(summoners_id_list)
with open("raw_data.txt", "w") as f:
	json.dump(raw_data, f)

#with open("raw_data.txt", "r") as f:
#	raw_data = json.load(f)

csv = RawToCSV(raw_data)
csv.Write()