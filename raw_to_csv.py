import json


class RawToCSV():
	def __init__(self, raw_data):
		self.classes_samples = {"MID":[], "JUNGLE":[], "TOP":[], "ADC":[], "SUPPORT":[]}
		self.unknown_samples = []
		self.labels = {"MID":"1", "JUNGLE":"2", "TOP":"3", "ADC":"4", "SUPPORT":"5", "UNKNOWN":"0"}

		self.__separate_samples(raw_data)
		return


	def __separate_samples(self, raw_data):
		for summoner in raw_data:
			role = raw_data[summoner][0]
			summoner_attributes = raw_data[summoner][1]
			
			if role == "UNKNOWN":
				self.unknown_samples.append(summoner_attributes)
			else:
				self.classes_samples[role].append(summoner_attributes)
		return


	def Write(self):
		lines = ["ROLE, TOTAL_SESSIONS, TOTAL_CHAMP_KILL, TOTAL_DEATHS, TOTAL_ASSISTS, TOTAL_MINION_KILLS, TOTAL_NEUTRAL_MINIONS, TOTAL_DAMAGE_DEALT, TOTAL_DAMAGE_TAKEN, TOTAL_GOLD_EARNED\
, TOTAL_HEAL, TOTAL_MAGIC_DAMAGE_DEALT, TOTAL_PHYSICAL_DAMAGE_DEALT, TOTAL_DOUBLE_KILLS, TOTAL_FIRST_BLOOD, TOTAL_PENTA_KILLS, TOTAL_QUADRA_KILLS, TOTAL_TRIPLE_KILLS, TOTAL_TURRETS_KILLED\
, TOTAL_UNREAL_KILLS\n"]


		for role in self.classes_samples:
			for sample in self.classes_samples[role]:
				line = role
				for attribute in sample:
					line += ", " + str(attribute)
				lines.append(line + "\n")

		for sample in self.unknown_samples:
			line = "UNKNOWN"
			for attribute in sample:
				line += ", " + str(attribute)
			lines.append(line + "\n")

		with open("lol_data.csv", "w") as data_file:
			data_file.writelines(lines)

		return



with open("raw_data.txt", "r") as f:
	raw_data = json.load(f)

csv = RawToCSV(raw_data)
csv.Write()