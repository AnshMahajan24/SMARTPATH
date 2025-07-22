from backend.geo_distance import get_coordinates, get_distance  # reuse your existing functions
import itertools

def auto_generate_routes(addresses):
    routes = []
    coords_map = {}

    # Step 1: Get coordinates for all addresses
    for address in addresses:
        coords = get_coordinates(address)
        if coords:
            coords_map[address] = coords
        else:
            print(f"❌ Skipping: {address} (Invalid or not found)")

    # Step 2: For each pair, get real distance from ORS
    for addr1, addr2 in itertools.combinations(addresses, 2):
        if addr1 in coords_map and addr2 in coords_map:
            dist = get_distance(coords_map[addr1], coords_map[addr2])
            if dist is not None:  # ✅ Fix for None distance
                routes.append((addr1, addr2, dist))
            else:
                print(f"⚠️ Skipping route {addr1} ↔ {addr2} (Distance fetch failed)")

    return routes

# ✅ Run test if this file is run directly
if __name__ == "__main__":
    locations = ["Pathankot, Punjab", "Kathua, Jammu", "Amritsar, Punjab"]
    routes = auto_generate_routes(locations)
    print(routes)
