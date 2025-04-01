import json
def is_point_inside_polygon(x, y, polygon):
    """
    Determines if a point (x, y) is inside a given polygon using the Ray-Casting method.
    """
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x or x <= xinters:
                inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def getFences(x, y, geometry):
    box_list = []
    for i in geometry:
        if is_point_inside_polygon(x, y, i["geometry"]):
            box_list.append(i["properties"]["name"])
            
    return box_list


import pandas as pd
def divideDataFrame(df, features, reset_sensitivity=2):
    """
    Divides a DataFrame into multiple DataFrames based on the zones defined in the geometry.
    Each zone will contain the rows that fall within its boundaries.
    """
        
    zone_dict = {} 
    final_zone_dict = {}
    zone_last_seen = {}
    index_counter = 0

    if "Latitude|Degrees|-180.0|180.0|25" not in df.columns or "Longitude|Degrees|-180.0|180.0|25" not in df.columns:
        raise ValueError("Latitude or Longitude column missing in DataFrame.")

    # Process each row in the DataFrame
    for _, row in df.iterrows():
        y = row["Latitude|Degrees|-180.0|180.0|25"]
        x = row["Longitude|Degrees|-180.0|180.0|25"]

        if pd.isna(x) or pd.isna(y):
            continue 

        areas = getFences(x, y, features)

        for area in areas:
            if area in zone_last_seen:
            
                if index_counter - zone_last_seen[area] > reset_sensitivity:
                    # Save the current data to final_zone_dict before resetting
                    if area not in final_zone_dict:
                        final_zone_dict[area] = []

                    final_zone_dict[area].append(pd.DataFrame(zone_dict[area]))  # Store previous data segment
                    zone_dict[area] = []

            # Update last seen valid index
            zone_last_seen[area] = index_counter

            # Add row to zone_dict
            if area not in zone_dict:
                zone_dict[area] = []
            zone_dict[area].append(row.to_dict())

        if areas:
            index_counter += 1 

    # At the end, save remaining data in zone_dict to final_zone_dict
    for zone, rows in zone_dict.items():
        if zone not in final_zone_dict:
            final_zone_dict[zone] = []
        final_zone_dict[zone].append(pd.DataFrame(rows))
        
    return final_zone_dict