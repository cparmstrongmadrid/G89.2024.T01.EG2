""" Class HotelStay (GE2.2) """
from datetime import datetime
from datetime import timedelta
import hashlib
import json
import os
from .hotel_management_exception import HotelManagementException
from pathlib import Path



def readDataFromJson(fi, encoding="utf-8"):
    try:
        with open(fi, encoding=encoding, mode='r') as f_base:
            data = json.load(f_base)
    except FileNotFoundError as e:
        raise HotelManagementException("The data file cannot be found.") from e
    except json.JSONDecodeError:  # raise
        data = []
    return data


def guestArrival(inputFile):
    """check file exists"""
    try:
        with open(inputFile, encoding="utf-8", mode='r') as f:
            data = json.load(f)
    except FileNotFoundError as e:
        raise HotelManagementException("The data file cannot be found.") from e
    except json.JSONDecodeError as e2:  # raise
        raise HotelManagementException("The file is not in JSON format.") from e2
    if not isinstance(data, dict):
        raise HotelManagementException("The JSON does not have the expected structure.")

    current = ""
    try:
        localizer = data.get("Localizer")
        id_card = data.get("IdCard")
        if not isinstance(id_card, str) or not isinstance(localizer, str):
            raise HotelManagementException("The JSON data does not have valid values.")
    except AttributeError as esc:
        raise HotelManagementException("The JSON does not have the expected structure.") from esc

    __path_data = str(Path.home()) + "/Documents/PycharmProjects/G89.2024.T01.EG2TWO/src/main/python/uc3m_travel/data"
    file_name = 'hotel_reservations.json'
    file_path = os.path.join(__path_data, file_name)
    hotel_data = readDataFromJson(file_path)
    # check localizer exists in hotel_data, then that ID matches
    loc_found = False
    id_found = False
    for stay in hotel_data:
        if localizer == stay["Localizer"]:
            loc_found = True
            if id_card == stay["id_card"]:
                id_found = True
                # check if dates are right here
                arrival = stay["arrival_date"]
                num_days = stay["num_days"]
                arrival_date = datetime.strptime(arrival, "%d/%m/%Y")
                current_datetime = datetime.now()
                if current_datetime != arrival_date:
                    raise HotelManagementException("The arrival date does not correspond to the reservation date.")
                current = HotelStay(id_card, localizer, num_days, stay["room_type"])
    if not id_found or not loc_found:
        raise HotelManagementException("The locator does not correspond to the stored data")

    # Creates a file that includes the data with all the processed stays.
    # write_file_path = os.path.join(adjacent_dir, 'hotel_stay_output.json')
    current.write_to_file(file_path)

    # Returns hexadecimal string with the room key (HM-FR-02-O1)
    return current.hex_str





class HotelStay:
    """Custom class for hotel stays."""

    def __init__(self, idcard, localizer, numDays, roomType):
        self.__alg = "SHA-256"
        self.__type = roomType
        self.__idcard = idcard
        self.__localizer = localizer
        justnow = datetime.utcnow()
        self.__arrival = justnow
        # timestamp is represented in seconds.miliseconds
        # to add the number of days we must express numdays in seconds
        self.departure = self.__arrival + timedelta(days=int(numDays))
        self.hex_str = hashlib.sha256(self.__signature_string().encode()).hexdigest()

    def __signature_string(self):
        """Composes the string to be used for generating the key for the room"""
        arrival_str = self.__arrival.strftime("%d/%m/%Y")
        departure_str = self.departure.strftime("%d/%m/%Y")

        return "{alg:" + self.__alg + ",typ:" + self.__type + ",localizer:" + \
            self.__localizer + ",arrival:" + arrival_str + \
            ",departure:" + departure_str + "}"

    @property
    def id_card(self):
        """Property that represents the product_id of the patient"""
        return self.__idcard

    @id_card.setter
    def id_card(self, value):
        self.__idcard = value

    @property
    def localizer(self):
        """Property that represents the order_id"""
        return self.__localizer

    @localizer.setter
    def localizer(self, value):
        self.__localizer = value

    @property
    def arrival(self):
        """Property that represents the phone number of the client"""
        return self.__arrival

    @property
    def room_key(self):
        """Returns the sha256 signature of the date"""
        return hashlib.sha256(self.__signature_string().encode()).hexdigest()

    @property
    def departure(self):
        """Returns the issued at value"""
        return self.__departure

    @departure.setter
    def departure(self, value):
        self.__departure = value

    def to_dict(self):
        """Convert the HotelStay instance to a dictionary."""
        return {
            "Algorithm": self.__alg,
            "Type": self.__type,
            "IdCard": self.__idcard,
            "Localizer": self.__localizer,
            "Arrival": self.__arrival.isoformat(),
            "Departure": self.__departure.isoformat(),
            "Signature": self.hex_str
        }

    def write_to_file(self, filename):
        """Write the HotelStay data to a JSON file."""
        data = self.to_dict()
        try:
            with open(filename, 'r', encoding="utf-8") as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            existing_data = []
        except json.JSONDecodeError:
            existing_data = []

        existing_data.append(data)

        with open(filename, 'w', encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4)
