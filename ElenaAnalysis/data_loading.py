import os
import pandas as pd
pd.options.mode.chained_assignment = None
from datetime import datetime, timedelta
import yaml


class LoadData(object):
    """
    class which takes care the loading of all files
    """
    def __init__(self,
                 data_path,
                 config_file=None):
        self._data_path = data_path
        self._excretion_csv = os.path.join(self._data_path, "excretions.csv")
        self._feed_csv = os.path.join(self._data_path, "feeds.csv")
        self._poo_pkl = os.path.join(self._data_path, "poo.pkl")
        self._pee_pkl = os.path.join(self._data_path, "pee.pkl")
        self._feed_pkl = os.path.join(self._data_path, "feed.pkl")

        self._converting_dict_pee = dict()
        self._converting_dict_poo = dict()
        self._config_file = config_file
        self._load_config()

        self._df = self.read_csv(self._excretion_csv)
        self._df_feed = self.read_csv(self._feed_csv)

    def read_csv(self, path):
        df = pd.read_csv(path)
        df.columns = [col.replace(" ", "") for col in df.columns]
        return df

    def _load_config(self):
        print("Reading config...")
        if self._config_file is not None:
            with open(self._config_file, 'r') as stream:
                try:
                    self.config = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
            self._converting_dict_pee = self.config["converting_dict_pee"]
            self._converting_dict_poo = self.config["converting_dict_poo"]
            self._numbers_config = self.config["numbers_config"]
        else:
            self.config = None

    def load_data(self):
        self._df_pee = self.process_pee()
        self._df_poo = self.process_poo()
        self._df_feed = self.process_feed()

    def _add_mica(self, dict_Note):
        try:
            return dict_Note["Mica"]
        except KeyError:
            return None

    def _add_windel(self, dict_Note):
        try:
            return dict_Note["Windel"]
        except KeyError:
            return None


    def _convert_notes_pee(self, note):
        try:
            mod_note = note.lower()
            if mod_note in self._converting_dict_pee.keys():
                return self._converting_dict_pee[mod_note]
            else:
                return mod_note
        except:
            return "None"

    def _process_converted_notes(self, note):
        if note != "None":
            mod_note = note.split(",")
            converted_dict = dict()
            try:
                for element in note.split(', '):
                    #  print(element)
                    x = element.split(': ')[0]
                    y = element.split(': ')[1]
                    if y.strip().lower() == "true" or y.strip().lower() == "false":
                        converted_dict[x.strip()] = y.strip().lower() == "true"
                    else:
                        converted_dict[x.strip()] = y.strip()
            except:
                print("Cannot convert", note, "to dict --> Adjust your config!")

            return converted_dict
        else:
            return {"Mica": None, "Windel": None}

    def process_pee(self):
        df_pee = self._df[self._df["Type"] == "Pee"]
        df_pee["mod_Notes"] = df_pee.apply(
            lambda x: self._convert_notes_pee(x["Notes"]), axis=1)
        df_pee["dict_Notes"] = df_pee.apply(
            lambda x: self._process_converted_notes(x["mod_Notes"]), axis=1)
        df_pee["Mica"] = df_pee.apply(
            lambda x: self._add_mica(x["dict_Notes"]), axis=1)
        df_pee["Windel"] = df_pee.apply(
            lambda x: self._add_windel(x["dict_Notes"]), axis=1)
        df_pee["datetime"] = df_pee.apply(
            lambda x: datetime.strptime(x["Time"], '%H:%M:%S %m-%d-%Y'),
            axis=1)

        filename = self._pee_pkl
        print(f"Writing {filename}")
        df_pee.to_pickle(filename)
        return df_pee

    def _convert_notes_poo(self, note):
        try:
            mod_note = note.lower()
            lower_keys = [
                item.lower() for item in self._converting_dict_poo.keys()
            ]
            if mod_note in lower_keys:
                return self._converting_dict_poo[note]
            else:
                return mod_note
        except:
            return "None"

    def process_poo(self):
        df_poo = self._df[(self._df["Type"] == "Poo") |
                          (self._df["Type"] == "Pee and Poo")]
        df_poo["mod_Notes"] = df_poo.apply(
            lambda x: self._convert_notes_poo(x["Notes"]), axis=1)
        df_poo["dict_Notes"] = df_poo.apply(
            lambda x: self._process_converted_notes(x["mod_Notes"]), axis=1)

        filename = self._poo_pkl
        print(f"Writing {filename}")
        df_poo.to_pickle(filename)
        return df_poo

    def process_feed(self):
        df_feed = self._df_feed
        df_feed["start"] = df_feed.apply(lambda x: datetime.strptime(x["StartTime"], '%H:%M:%S %m-%d-%Y'), axis=1)
        df_feed["end"] = df_feed.apply(lambda x: datetime.strptime(x["EndTime"], '%H:%M:%S %m-%d-%Y'), axis=1)

        filename = self._feed_pkl
        print(f"Writing {filename}")
        df_feed.to_pickle(filename)
        return df_feed

