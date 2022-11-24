
_AREA_DETAILS = {
    "III": ["1","2","PMH","bình thạnh","binh thanh"],
    "II": ["9","thủ đức","thu duc"]
}

_WARDS_IN_SPECIAL_AREA = {
    "Q2":["An Phú","Thảo Điền","An Khánh","Bình Khánh","Bình An","Thủ Thiêm","An Lợi Đông","Bình Trưng Tây",
        "Bình Trưng Đông","Cát Lái","Thạnh Mỹ Lợi"],
    "Q9": ["Hiệp Phú","Long Bình","Long Phước","Long Thạnh Mỹ","Long Trường","Phú Hữu","Phước Bình",
        "Phước Long A","Phước Long B","Tân Phú","Tăng Nhơn Phú A","Tăng Nhơn Phú B","Trường Thạnh"],
    "PMH": ["Tân Phú","Tân Phong","Tân Hưng"]
}

_DISTRICT_WITH_NAME = ["Bình Tân","Bình Thạnh","Gò Vấp","Phú Nhuận","Tân Bình","Tân Phú","Thủ Đức",
"Bình Chánh","Cần Giờ","Củ Chi","Hóc Môn","Nhà Bè"]

_DISTRICT_WITH_NAME_WITHOUT_ACCENT = ["Binh Tan","Binh Thanh","Go Vap","Phu Nhuan","Tan Binh","Tan Phu",
"Thu Đuc","Binh Chanh","Can Gio","Cu Chi","Hoc Mon","Nha Be",]

def get_area_from_district(district_fullname, address):
    district = district_fullname.lower()
    district = district.replace("quận","")
    district = district.replace("huyện","")
    district = district.replace("district","")
    district = district.strip()
    if district == "7":
        area, district_fullname = get_area_for_district_7(district,district_fullname,address)
    else :
        area = get_location_area(district)

    return area, district_fullname


def get_location_area(district):
    area_found = "I"
    for area in _AREA_DETAILS.keys():
        if district in _AREA_DETAILS[area]:
            area_found = area
    return area_found

def get_area_for_district_7(district,district_fullname,address):
    if address != None:
        address = address.lower()
        address = ' '.join(address.split())
        for ward in _WARDS_IN_SPECIAL_AREA["PMH"]:
            if ward.lower() in address:
                district = "PMH"
                district_fullname = "Phú Mỹ Hưng, " + district_fullname
                break;
    area = get_location_area(district)
    return area, district_fullname

def get_district_from_address(address):
    district_found = "unknown"
    address = address.lower()
    short_address = ' '.join(address.split())
    if "thành phố thủ đức" in short_address:
        district_found = "Quận Thủ Đức"
        for ward in _WARDS_IN_SPECIAL_AREA["Q2"]:
            if ward.lower().replace(" ","") in lower_address:
                district_found = "Quận 2"
                break
        if district_found == "Quận Thủ Đức":
            for ward in _WARDS_IN_SPECIAL_AREA["Q9"]:
                if ward.lower().replace(" ","") in lower_address:
                    district_found = "Quận 9"
                    break
        return district_found

    address_list = address.split(",")
    district_item_found = False
    for item in address_list:
        item = item.strip()
        if "quận" in item or "huyện" in item or "district" in item:
            item = ' '.join(item.split())
            district_found = item.title()
            return district_found

    for district in _DISTRICT_WITH_NAME:
        if district.lower() in short_address:
            district_found = district.title()
            return district_found

    for district in _DISTRICT_WITH_NAME_WITHOUT_ACCENT:
        if district.lower() in short_address:
            district_found = district.title()
            return district_found

    return district_found
