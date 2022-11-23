
_AREA_DETAILS = {
    "III": ["1","2","PMH","bìnhthạnh","binhthanh"],
    "II": ["9","thủđức","thuduc"]
}

_WARDS_IN_SPECIAL_AREA = {
    "Q2":["An Phú","Thảo Điền","An Khánh","Bình Khánh","Bình An","Thủ Thiêm","An Lợi Đông","Bình Trưng Tây",
        "Bình Trưng Đông","Cát Lái","Thạnh Mỹ Lợi"],
    "Q9": ["Hiệp Phú","Long Bình","Long Phước","Long Thạnh Mỹ","Long Trường","Phú Hữu","Phước Bình",
        "Phước Long A","Phước Long B","Tân Phú","Tăng Nhơn Phú A","Tăng Nhơn Phú B","Trường Thạnh"],
    "PMH": ["Tân Phú","Tân Phong","Tân Hưng"]
}

def get_location_area(district):
    area_found = "I"
    for area in _AREA_DETAILS.keys():
        if district in _AREA_DETAILS[area]:
            area_found = area
    return area_found


def get_district(address):
    area_found =  "I"
    district_found = "unknown"
    lower_address = address.lower().replace(" ","")
    if "thành phố thủ đức".replace(" ","") in lower_address:
        area_found = "II"
        district_found = "Quận Thủ Đức"
        for ward in _WARDS_IN_SPECIAL_AREA["Q2"]:
            if ward.lower().replace(" ","") in lower_address:
                area_found = "III"
                district_found = "Quận 2"
                break
        if area_found == "II":
            for ward in _WARDS_IN_SPECIAL_AREA["Q9"]:
                if ward.lower().replace(" ","") in lower_address:
                    district_found = "Quận 9"
                    break
        return area_found, district_found

    address_list = address.lower().split(",")
    district_item_found = False
    for item in address_list:
        if "quận" in item:
            district = item.replace("quận","").replace(" ","")
            #district_found = "Quận " + district
            district_found = item.title().lstrip().rstrip()
            district_item_found = True
        elif "district" in item:
            district = item.replace("district","").replace(" ","")
            #district_found = "District " + district
            district_found = item.title().lstrip().rstrip()
            district_item_found = True
        if district_item_found:
            if district == "7":
                for ward in _WARDS_IN_SPECIAL_AREA["PMH"]:
                    if ward.lower().replace(" ","") in lower_address:
                        print("PMH found: ", ward, district)
                        district = "PMH"
                        district_found = "Phú Mỹ Hưng, " + district_found
                        break
            area_found = get_location_area(district)
            return area_found, district_found

    return area_found, district_found
