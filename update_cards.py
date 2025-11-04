# Directions: To get the output of rules updates in a markdown file, make sure that you have the below libraries installed,
# then run the following command in the terminal in the directory this file is in: `python update_cards.py`

# Required libraries. To install, run: `pip install requests` and `pip install datetime` (windows)
# requests is for getting the data from the API
# datetime is for comparing dates to show rulings from newest to oldest
import requests
import datetime
import json
import time

# Data overrides that help when different variants of the same card have different information in the official database.
data_overrides = {
    "ANAKIN SKYWALKER - WHAT IT TAKES TO WIN": {
        'keywords': ["Overwhelm"]
    },
    "ASAJJ VENTRESS - COUNT DOOKU'S ASSASSIN": {
        'unique': 1
    },
    "BOBA FETT - COLLECTING THE BOUNTY": {
        'aspects': ["Cunning", "Villainy"]
    },
    "BOSSK - DEADLY STALKER": {
        'aspects': ["Cunning", "Villainy"]
    },
    "CHANCELLOR PALPATINE - PLAYING BOTH SIDES": {
        'aspects': ["Cunning", "Heroism", "Villainy"]
    },
    "CORPORATE LIGHT CRUISER": {
        'keywords': ["Ambush", "Raid"]
    },
    "COUNT DOOKU - FACE OF THE CONFEDERACY": {
        'keywords': ["Overwhelm", "Exploit"]
    },
    "EXPERIENCE": {
        'types': ["Token Upgrade"],
        'upgradeHp': 1,
        'upgradePower': 1,
        'hp': None,
        'power': None
    },
    "HARDPOINT HEAVY BLASTER": {
        'types': ["Upgrade"],
        'upgradeHp': 2,
        'upgradePower': 2,
        'hp': 'null',
        'power': 'null'
    },
    "HOTSHOT DL-44 BLASTER": {
        'upgradePower': 2
    },
    "IT BINDS ALL THINGS": {
        'aspects': ["Vigilance"]
    },
    "KYLO REN - KILLING THE PAST": {
        'unique': 1
    },
    "LANDO CALRISSIAN - WITH IMPECCABLE TASTE": {
        'hp': 5,
        'power': 2
    },
    "MC30 ASSAULT FRIGATE": {
        'keywords': ["Overwhelm", "Raid"]
    },
    "PRE VIZSLA - PURSUING THE THRONE": {
        'keywords': ["Saboteur"]
    },
    "R2-D2 - FULL OF SOLUTIONS": {
        'subtitle': 'Full of Solutions'
    },
    "SIDON ITHANO - THE CRIMSON CORSAIR": {
        'upgradeHp': -2,
        'upgradePower': -2
    },
    "THE MANDALORIAN'S RIFLE": {
        'unique': 1,
        'upgradePower': 3
    },
    "VONREG'S TIE INTERCEPTOR - ACE OF THE FIRST ORDER": {
        'keywords': ["Overwhelm", "Raid"]
    },
    "WRECKER - BOOM!": {
        'subtitle': "BOOM!"
    }
}

# Add sorting for variants. Uses .append() for readability and easy adjustments to variant order (although this really shouldn't need to change).
variant_order = []
variant_order.append("Standard")
variant_order.append("Standard Foil")
variant_order.append("Hyperspace")
variant_order.append("Hyperspace Foil")
variant_order.append("Showcase")
variant_order.append("Standard Prestige")
variant_order.append("Foil Prestige")
variant_order.append("Serialized Prestige")
variant_order.append("Prerelease Promo")
variant_order.append("Prerelease Judge")
variant_order.append("OP Promo")
variant_order.append("Weekly Play")
variant_order.append("OP Promo Foil")
variant_order.append("Weekly Play Foil")
variant_order.append("OP Judge")
variant_order.append("Judge Program")
variant_order.append("OP Top 16")
variant_order.append("OP Top 8")
variant_order.append("OP Top 4")
variant_order.append("OP Finalist")
variant_order.append("OP Champion")
variant_order.append("SS Judge")
variant_order.append("SS Participation")
variant_order.append("SS Top 8")
variant_order.append("SS Top 4")
variant_order.append("SS Finalist")
variant_order.append("SS Champion")
variant_order.append("PQ Judge")
variant_order.append("PQ Participation")
variant_order.append("PQ Top 16")
variant_order.append("PQ Top 8")
variant_order.append("PQ Top 4")
variant_order.append("PQ Finalist")
variant_order.append("PQ Champion")
variant_order.append("SQ Judge")
variant_order.append("SQ Participation")
variant_order.append("SQ Prize Wall")
variant_order.append("SQ Event Pack")
variant_order.append("SQ Day Two")
variant_order.append("SQ Top 8")
variant_order.append("SQ Top 4")
variant_order.append("SQ Finalist")
variant_order.append("SQ Champion")
variant_order.append("RQ Judge")
variant_order.append("RQ Participation")
variant_order.append("RQ Prize Wall")
variant_order.append("RQ Event Pack")
variant_order.append("RQ Day Two")
variant_order.append("RQ Top 8")
variant_order.append("RQ Top 4")
variant_order.append("RQ Finalist")
variant_order.append("RQ Champion")
variant_order.append("GC Judge")
variant_order.append("GC Participation")
variant_order.append("GC VIP Promo")
variant_order.append("GC Prize Wall")
variant_order.append("GC Event Pack")
variant_order.append("GC Day Three")
variant_order.append("GC Top 64")
variant_order.append("GC Top 8")
variant_order.append("GC Top 4")
variant_order.append("GC Finalist")
variant_order.append("GC Champion")
variant_order.append("Event Exclusive")
variant_order.append("Convention Exclusive")

# Function to get all cards from the SWU API
# Returns an array of card objects and their associated data
def get_card_data():
    # Set a couple of the requests parameters to make the API call more efficient
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=12)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # Set the url of the API call - this is the same between getting the total page count and getting the card data itself.
    api_url = 'https://admin.starwarsunlimited.com/api/cards'
    # Initial call directly to the url to get the page count
    response = session.get(api_url)

    total_pages = response.json()['meta']['pagination']['pageCount']

    print(f'Total number of pages: {total_pages}.')

    # Keep track of all of the cards in this fancy shmancy array
    cards = []
    if total_pages > 0:
        # Get the card data from each page and add that page to an array of pages
        pages = []
        for i in range(1, total_pages + 1):
            retry_count = 0
            max_retries = 10
            page_url = f'{api_url}?locale=en&pagination[page]={i}'

            while retry_count < max_retries:
                try:
                    response = session.get(page_url)
                    response.raise_for_status()
                    pages.append(response.json()['data'])
                    print(f'Finished page {i} of {total_pages}.')
                    break
                except (requests.exceptions.RequestException, json.JSONDecodeError):
                    retry_count += 1
                    print(f'Error occurred while fetching page {i}. Retrying...')
            else:
                print(f'Failed to fetch page {i} after {max_retries} retries.')
                raise Exception(f'Failed to fetch page {i} after {max_retries} retries.')

        # Smush the pages into a single array
        cards = [item for sublist in pages for item in sublist]
        print(f'Finished putting together the pages of card data.')

    return cards

# Function to get set information like order and main sets from the card data
# Takes in an array of card objects
# Returns an object containing a set number to set name dictionary and an array of main set numbers
def get_set_data(cards):
    # Use this object to keep track of the match between a set number and the name of the set
    sets = {}
    # Use this object to keep track of the match between a set number and the abbreviation of the set
    set_abbrs = {}
    # Use this array to keep track of the main set numbers that we care about (see below)
    set_numbers = []

    # Loop through each one of the cards
    for card in cards:
        card_data = card["attributes"]
        card_set = card_data["expansion"]["data"]["attributes"]
        set_name = card_set["name"]
        set_number = card_set["sortValue"]
        set_abbr = card_set["code"]
        
        # The main sets (like SOR, SHD, TWI, etc) all have set numbers that end with a '9', whereas other sets end with something else.
        if set_number % 10 == 9 or set_number == 61:
            # We only want to add each set once
            if str(set_number) not in sets:
                sets[str(set_number)] = set_name
                set_abbrs[str(set_number)] = set_abbr
                set_numbers.append(set_number)

    return {
        'sets': sets,
        'set_numbers': set_numbers,
        'set_abbrs': set_abbrs
    }

def get_aspect_data(cards):
    # Use this object to keep track of the match between an aspect name and it's sort order
    aspects = {}

    # Loop through each one of the cards
    for card in cards:
        card_data = card["attributes"]

        for aspect in card_data["aspects"]["data"]:
            if aspect["attributes"]["name"] != "" and aspect["attributes"]["name"] not in aspects:
                aspects[aspect["attributes"]["name"]] = aspect["attributes"]["sortValue"]
        for aspect in card_data["aspectDuplicates"]["data"]:
            if aspect["attributes"]["name"] != "" and aspect["attributes"]["name"] not in aspects:
                aspects[aspect["attributes"]["name"]] = aspect["attributes"]["sortValue"]

    aspectOrder = sorted(aspects, key=aspects.get)

    return aspectOrder

# Function to extract the rule data from the card array
# Takes in an array of card objects and an array of main set numbers
# Returns an object containing rules, a dictionary of card names to most recent main set printing, and dates for batch updates
def get_rule_data(cards, set_numbers):
    # Use this object to keep track of the rules, using the card name as the key and a multi-dimensional array for it's associated rules
    rules = {}
    # Use this object to keep track of the most recent set reprint for each card
    card_location = {}
    # Keep track of the dates that rulings were added since they appear to all show up in batches.
    dates = []

    print(f'Starting rules build.')
    # Loop through each one of the cards
    for card in cards:
        card_data = card["attributes"]
        # Checking the title and subtitle in all caps to check for any data overrides.
        card_id_caps = f'{card_data["title"]}{" - " + card_data["subtitle"] if card_data["subtitle"] is not None and card_data["subtitle"] != "" else ""}'.upper()
        subtitle = card_data["subtitle"]
        if card_id_caps in data_overrides:
            if "subtitle" in data_overrides[card_id_caps]:
                subtitle = data_overrides[card_id_caps]["subtitle"]
        # This is just the best way so far that has been found to get unique versions of cards (like keeping both Darth Maul units separate)
        card_id = f'{card_data["title"]}{" - " + subtitle if subtitle is not None and subtitle != "" else ""}'
        
        # We only care if the card has any additional rulings
        if card_data["rulesStyled"] is not None and card_data["rulesStyled"] != '':
            # And we only care if the card we are looking at is in one of the main sets that we've identified
            if card_data["expansion"]["data"]["attributes"]["sortValue"] in set_numbers:
                # Keep track of the set this version was printed in for later
                if card_id.upper() not in card_location:
                    card_location[card_id.upper()] = card_data["expansion"]["data"]["attributes"]["sortValue"]

                if card_data["expansion"]["data"]["attributes"]["sortValue"] > card_location[card_id.upper()]:
                    card_location[card_id.upper()] = card_data["expansion"]["data"]["attributes"]["sortValue"]

                # The RulesStyled field is a long string with HTML, so we want to do our best to try and strip all of that from our data.
                rules_string = card_data["rulesStyled"].replace('\n        ', '')
                # Each <tr> should indicate a new row on the additional rules table, and thus a separate rule.
                rules_array = rules_string.split('<tr>')

                # Loop through each rule for the card variant we are looking at
                for rule in rules_array:
                    # A <td> indicates a new column in the table. There are two columns: date and rule
                    rule_array = rule.split('<td>')

                    # Clean some of the rules information and add it to the rules for the card if that rule has not already been added to that card
                    if len(rule_array) > 1:
                        rule_final = []

                        for rule_item in rule_array:
                            if rule_item != '':
                                rule_final.append(rule_item.replace('</td>', '').split('</tr>')[0])

                        if card_id.upper() not in rules:
                            rules[card_id.upper()] = []

                        if rule_final[0] not in dates:
                            dates.append(rule_final[0])

                        exists = any(sub_arr == rule_final for sub_arr in rules[card_id.upper()])
                        if exists is not True:
                            rules[card_id.upper()].append(rule_final)

    print(f'Finished rules build.')
    return {
        'rules': rules,
        'card_location': card_location,
        'dates': dates
    }

def get_flat_data(cards, rules, sets, aspects):
    flat_data = {}

    for card in cards:
        card_data = card["attributes"]

        # Checking the title and subtitle in all caps to check for any data overrides.
        card_id_caps = f'{card_data["title"]}{" - " + card_data["subtitle"] if card_data["subtitle"] is not None and card_data["subtitle"] != "" else ""}'.upper()
        subtitle = card_data["subtitle"]
        if card_id_caps in data_overrides:
            if "subtitle" in data_overrides[card_id_caps]:
                subtitle = data_overrides[card_id_caps]["subtitle"]
        
        card_id = f'{card_data["title"]}{" - " + subtitle if subtitle is not None and subtitle != "" else ""}'
        card_id_caps = card_id.upper()        

        if card_id not in flat_data:
            flat_data[card_id] = {
                "card_name": card_id,
                "versions": [],
                "rules": [],
                "aspects": [],
                "aspectDuplicates": [],
                "types": [],
                "sets": [],
                "traits": []
            }

        card_info = {
            "set": card_data["expansion"]["data"]["attributes"]["name"],
            "set_number": card_data["expansion"]["data"]["attributes"]["sortValue"],
            "deploy_box": card_data["deployBox"] if card_data["deployBox"] is not None and card_data["deployBox"] != "" else "",
            "epic_action": card_data["epicAction"] if card_data["epicAction"] is not None and card_data["epicAction"] != "" else "",
            "text": card_data["text"] if card_data["text"] is not None and card_data["text"] != "" else "",
            "front_image": card_data["artFront"]["data"]["attributes"]["formats"]["thumbnail"]["url"] if card_data["artFront"]["data"] is not None and card_data["artFront"]["data"]["attributes"]["formats"]["thumbnail"]["url"] != "" else "",
            "back_image": card_data["artBack"]["data"]["attributes"]["formats"]["thumbnail"]["url"] if card_data["artBack"]["data"] is not None and card_data["artBack"]["data"]["attributes"]["formats"]["thumbnail"]["url"] != "" else "",
            "front_orient": card_data["artFrontHorizontal"] if card_data["artFrontHorizontal"] is not None else "",
            "back_orient": card_data["artBackHorizontal"] if card_data["artBackHorizontal"] is not None else "",
            "variant_name": card_data["variantTypes"]["data"][0]["attributes"]["name"] if card_data["variantTypes"]["data"] is not None and len(card_data["variantTypes"]["data"]) > 0 else "",
        }

        for aspect in card_data["aspects"]["data"]:
            if aspect["attributes"]["name"] != "":
                flat_data[card_id]["aspects"].append(aspect["attributes"]["name"])
        for aspect in card_data["aspectDuplicates"]["data"]:
            if aspect["attributes"]["name"] != "":
                flat_data[card_id]["aspectDuplicates"].append(aspect["attributes"]["name"])

        if card_data["type"]["data"] is not None:
            if card_data["type"]["data"]["attributes"]["name"] != "":
                flat_data[card_id]["types"].append(card_data["type"]["data"]["attributes"]["name"])
        if card_data["type2"]["data"] is not None:
            if card_data["type2"]["data"]["attributes"]["name"] != "":
                flat_data[card_id]["types"].append(card_data["type2"]["data"]["attributes"]["name"])
        if card_id_caps in data_overrides:
            if "types" in data_overrides[card_id_caps]:
                flat_data[card_id]["types"] = data_overrides[card_id_caps]["types"]

        for trait in card_data["traits"]["data"]:
            if trait["attributes"]["name"] != "":
                flat_data[card_id]["traits"].append(trait["attributes"]["name"])
        if card_id_caps in data_overrides:
            if "traits" in data_overrides[card_id_caps]:
                flat_data[card_id]["traits"] = data_overrides[card_id_caps]["traits"]

        if str(card_data["expansion"]["data"]["attributes"]["sortValue"]) in sets:
            if str(card_data["expansion"]["data"]["attributes"]["sortValue"]) not in flat_data[card_id]["sets"]:
                flat_data[card_id]["sets"].append(str(card_data["expansion"]["data"]["attributes"]["sortValue"]))

        if card_id_caps in rules:
            flat_data[card_id]["rules"] = rules[card_id_caps]

        if card_info["variant_name"] != "":
            flat_data[card_id]["versions"].append(card_info)

    tidy_data = {}
    for id, info in flat_data.items():
        id_caps = id.upper()
        tidy_data[id] = {}
        tidy_data[id]["card_name"] = info["card_name"]
        tidy_data[id]["rules"] = info["rules"]

        tidy_data[id]["versions"] = sorted(info["versions"], key=lambda x: variant_order.index(x["variant_name"]))

        aspectFinal = []
        aspectDupe = []
        for aspect in info["aspects"]:
            if info["aspects"].count(aspect) >= len(info["versions"]) and aspect not in aspectFinal:
                aspectFinal.append(aspect)
        for aspect in info["aspectDuplicates"]:
            if info["aspectDuplicates"].count(aspect) >= len(info["versions"]) and aspect not in aspectDupe:
                aspectDupe.append(aspect)

        aspectFinal.extend(aspectDupe)
        
        aspectFinal = sorted(aspectFinal, key=lambda x: aspects.index(x))
        if id_caps in data_overrides:
            if "aspects" in data_overrides[id_caps]:
                aspectFinal = data_overrides[id_caps]["aspects"].copy()

        tidy_data[id]["aspects"] = aspectFinal

        cardType = ''
        typestring = "".join(info["types"]).lower()
        if 'leader' in typestring:
            cardType = "Leader"
        elif 'base' in typestring:
            cardType = "Base"
        elif 'unit' in typestring:
            cardType = "Unit"
        elif 'upgrade' in typestring:
            cardType = "Upgrade"
        elif 'event' in typestring:
            cardType = "Event"
        tidy_data[id]["type"] = cardType

        cardSets = sorted(info["sets"])
        setOrder = []
        for set in cardSets:
            setOrder.append(sets[set])
        tidy_data[id]["sets"] = setOrder

        tidy_data[id]["traits"] = ",".join(info["traits"])

    return tidy_data

# Function to export the rules to a markdown file
# Takes in an object containing rules, a dictionary of card names to main set printing, a dictionary of set names to set numbers,
    # an array of main set numbers, and an array of update dates
# Returns nothing, but creates an md file with the output at rules.md
def export_card_js(cards):
    print(f'Building the js file.')

    # Start writing the js file
    with open('cards_data.js', 'w', encoding='utf-8') as f:
        lines = [
            'window.projectNamespace = window.projectNamespace || {};\n',
            'projectNamespace.cardData = window.projectNamespace.cardData || [];\n',
            'projectNamespace.cardData = ' + json.dumps(cards) + ';'
        ]
        # Finish writing the file
        f.writelines(lines)

    print(f'File build has finished.')

# Function that is run when the script is called.
if __name__ == "__main__":
    # Get the card data from the API
    cards = get_card_data()

    if len(cards) > 0:
        # Extract the set data from the cards
        sets = get_set_data(cards)
        set_data = sets['sets']
        set_numbers = sets['set_numbers']
        set_abbrs = sets['set_abbrs']

        # Extract the additional rules from the cards
        rules = get_rule_data(cards, set_numbers)
        rules_info = rules['rules']
        card_location = rules['card_location']
        dates = rules['dates']

        aspects = get_aspect_data(cards)

        flat_data = get_flat_data(cards, rules_info, set_abbrs, aspects)


    if len(flat_data) > 0:
        # Build the markdown file
        export_card_js(flat_data)

    print('Completed execution!')