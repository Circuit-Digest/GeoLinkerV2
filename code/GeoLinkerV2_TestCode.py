import requests
import json
from datetime import datetime, timedelta
import time
import random
import math

# Configuration
API_KEY = "xxxxxxxxxxxx"
DEVICE_ID = "My Bike"
API_URL = "https://www.circuitdigest.cloud/geolinker"

def send_gps_data(device_id, timestamp, lat, lng, battery, speed=None):
    """
    Send GPS data to the API endpoint and display full response

    Args:
        device_id: Unique identifier for the GPS device
        timestamp: Current timestamp for the GPS reading
        lat: Latitude coordinate
        lng: Longitude coordinate
        battery: Battery level percentage
        speed: Speed in km/h (optional)

    Returns:
        API response or None if error occurs
    """
    # Prepare payload with sensor data
    payload_data = {
        "temperature": random.uniform(24.0, 32.0),  # Random temperature between 24-32°C
        "humidity": random.uniform(60, 80)          # Random humidity between 60-80%
    }

    if speed is not None:
        payload_data["speed"] = speed

    # Prepare main data structure for API
    data = {
        "device_id": device_id,
        "timestamp": [timestamp],
        "lat": [lat],
        "long": [lng],
        # "battery": [battery],     # Commented out as per original
        # "payload": [payload_data] # Commented out as per original
    }

    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        # Display the data being sent
        print(f"📤 Sending data:")
        print(f"    📄 Request Headers: {headers}")
        print(f"    📦 Request Body: {json.dumps(data, indent=2)}")

        response = requests.post(API_URL, json=data, headers=headers)
        status_icon = "✓" if response.status_code == 200 else "✗"

        # Display the response details
        print(f"{status_icon} {timestamp} | Lat: {lat:.6f} | Lng: {lng:.6f} | Speed: {speed or 0:2.0f} km/h | Battery: {battery}%")
        print(f"    📡 Response Status: {response.status_code}")
        print(f"    📄 Response Headers: {dict(response.headers)}")

        try:
            response_json = response.json()
            print(f"    📋 Response Body: {json.dumps(response_json, indent=2)}")
            return response_json
        except:
            print(f"    📋 Response Text: {response.text}")
            return response.text

    except Exception as e:
        print(f"✗ Error sending data: {e}")
        return None

def send_bulk_gps_data(device_id, timestamps, latitudes, longitudes, batteries, payloads):
    """
    Send all GPS data in one bulk POST request and display full response

    Args:
        device_id: Unique identifier for the GPS device
        timestamps: List of timestamps
        latitudes: List of latitude coordinates
        longitudes: List of longitude coordinates
        batteries: List of battery levels
        payloads: List of payload data

    Returns:
        API response or None if error occurs
    """
    data = {
        "device_id": device_id,
        "timestamp": timestamps,
        "lat": latitudes,
        "long": longitudes,
        "battery": batteries,
        "payload": payloads
    }

    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        print(f"\n📦 Sending bulk data with {len(timestamps)} points...")
        print(f"📊 Data size: {len(json.dumps(data))} characters")

        # Display the data being sent
        print(f"\n📤 Sending bulk data:")
        print(f"    📄 Request Headers: {headers}")
        print(f"    📦 Request Body (first 3 points):")
        sample_data = {
            "device_id": device_id,
            "timestamp": timestamps[:3],
            "lat": latitudes[:3],
            "long": longitudes[:3],
            "battery": batteries[:3],
            "payload": payloads[:3]
        }
        print(json.dumps(sample_data, indent=2))
        print(f"    (Showing first 3 of {len(timestamps)} points)")

        response = requests.post(API_URL, json=data, headers=headers)

        print(f"\n📡 Bulk Upload Response:")
        print(f"    Status Code: {response.status_code}")
        print(f"    Response Headers: {dict(response.headers)}")

        try:
            response_json = response.json()
            print(f"    Response Body: {json.dumps(response_json, indent=2)}")

            if response.status_code == 200:
                print("✅ Bulk data sent successfully!")
            else:
                print(f"❌ Error in bulk upload: Status {response.status_code}")

            return response_json
        except:
            print(f"    Response Text: {response.text}")
            if response.status_code == 200:
                print("✅ Bulk data sent successfully!")
            else:
                print(f"❌ Error in bulk upload: Status {response.status_code}")
            return response.text

    except Exception as e:
        print(f"❌ Exception during bulk upload: {e}")
        return None
def calculate_speed_between_points(lat1, lng1, lat2, lng2, time_diff_minutes):
    """
    Calculate speed between two GPS coordinates using Haversine formula
    """
    if time_diff_minutes <= 0:
        return 0

    # Earth's radius in kilometers
    R = 6371

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    # Haversine formula for great-circle distance
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance_km = R * c

    # Calculate speed and cap at 80 km/h for realistic city driving
    speed_kmh = (distance_km / time_diff_minutes) * 60
    return min(speed_kmh, 80)

def get_traffic_delay(hour, is_main_road=False):
    """Simulate traffic-based delays"""
    base_delay = 1.0
    if 8 <= hour <= 10:
        base_delay = 1.8 if is_main_road else 2.2
    elif 18 <= hour <= 20:
        base_delay = 2.0 if is_main_road else 2.5
    elif 15 <= hour <= 16:
        base_delay = 1.4 if is_main_road else 1.6
    elif 12 <= hour <= 14:
        base_delay = 1.2
    elif 22 <= hour or hour <= 6:
        base_delay = 0.7
    return base_delay * random.uniform(0.8, 1.3)

def get_journey_data():
    """
    Define the complete journey with GPS coordinates and context information
    """
    return [
        # Starting location and initial movement
        (11.010915301164033, 77.0132087643678, "Home - Journey Start", False),
        (11.010852113196895, 77.01297272998573, "Leaving home area", False),
        (11.011368147865086, 77.01284398395916, "Local road - heading to main road", False),

        # Connecting to main roads
        (11.012895183932189, 77.01271523793258, "Approaching main road connection", True),
        (11.013400683781928, 77.0126508649193, "Main road junction", True),
        (11.013432277493726, 77.01226462683955, "Main road - steady progress", True),

        # Main journey on primary roads
        (11.012768808834144, 77.00907816268172, "Major road section - good speed", True),
        (11.012831996389947, 77.00888504364185, "Continuing on main road", True),
        (11.01294784020703, 77.00871338227309, "Main road - approaching junction", True),
        (11.01306368397854, 77.00850953439766, "Junction area - slower traffic", True),

        # Navigating through complex areas
        (11.013253246415422, 77.0082305846734, "Navigating through junction", True),
        (11.013379621305521, 77.00788726193586, "Post-junction - picking up speed", True),
        (11.013400683781928, 77.00755466803386, "Main road - good traffic flow", True),
        (11.013116340223256, 77.0073830066651, "Approaching destination area", True),

        # Arriving at destination
        (11.012789871354238, 77.00712551461193, "Destination area - slower speeds", False),
        (11.012084276110311, 77.00710405694085, "Near destination - parking search", False),
        (11.011483992258128, 77.00720061646078, "Destination reached - parking", False),

        # Activity at destination
        (11.010567767176969, 77.007361548994, "Parked - short walk/activity", False),
        (11.010188638723273, 77.00772632940264, "Activity at destination", False),

        # Starting return journey
        (11.009999074313392, 77.0082949576867, "Preparing to leave destination", False),
        (11.009588351006704, 77.0090996203528, "Starting return journey", False),
        (11.009630476500412, 77.00924982405049, "Return route - local roads", False),
        (11.009641007872897, 77.00934638357042, "Return route progress", False),
        (11.009672601988104, 77.0094107565837, "Return route - slow section", False),
        (11.009672601988104, 77.0094965872681, "Traffic light/stop", False),

        # Return journey main sections
        (11.009806413371894, 77.01042480446029, "Return route - main road access", True),
        (11.009668649605482, 77.00984427871586, "Return via alternate route", True),
        (11.009574719727805, 77.00914254429954, "Return journey - main section", True),
        (11.009317977909296, 77.0091935795298, "Return journey continues", True),
        (11.009023663841996, 77.00925737356766, "Return - steady progress", True),

        # Return journey through different areas
        (11.007991322505761, 77.00951042346873, "Return route - different path", True),
        (11.007640648812478, 77.00985491127311, "Return journey - avoiding traffic", True),
        (11.007302498784261, 77.01039078119103, "Return route - side roads", False),
        (11.007026968844638, 77.01119458606792, "Return - residential area approach", False),
        (11.00680779711771, 77.01218339365457, "Return - navigating local roads", False),

        # Final approach to home
        (11.00703323089158, 77.01391221208027, "Return - longer route taken", False),
        (11.007678221013876, 77.01345927441155, "Return - heading towards home area", False),
        (11.008417140020423, 77.01333168636238, "Return - approaching home locality", False),
        (11.009037079096183, 77.01320409828668, "Return - familiar roads", False),
        (11.009368965151896, 77.01313392485663, "Return - almost home", False),
        (11.009857400529931, 77.01313392485663, "Return - final approach", False),
        (11.009882448476192, 77.01332530697017, "Return - entering home area", False),
        (11.010045260075, 77.01359962133293, "Return - home locality", False),
        (11.010427240780418, 77.01384203867676, "Return - very close to home", False),
        (11.010665195723483, 77.01434601157575, "Return - final street", False),
        (11.010871840649608, 77.01433325276818, "Return - parking area", False),
        (11.011084747391523, 77.01421842350005, "Return - almost parked", False),
        (11.010959508150215, 77.01355496550643, "Return - final positioning", False),
        (11.01092819833156, 77.01342737743073, "Return - parking maneuver", False),
        (11.010890626544791, 77.0132678923361, "Home - Journey Complete", False)
    ]

def send_bulk_journey_data():
    """
    Prepare all journey data and send in one bulk API call (based on second code)
    """
    print("📤 BULK DATA UPLOAD MODE")
    print("=" * 60)

    journey_data = get_journey_data()
    start_time = datetime.now().replace(hour=14, minute=30, second=0, microsecond=0)
    current_time = start_time
    battery_level = 87

    timestamps, latitudes, longitudes, batteries, payloads = [], [], [], [], []

    print(f"📊 Preparing {len(journey_data)} GPS points for bulk upload...")

    for i, (lat, lng, description, is_main_road) in enumerate(journey_data):

        if i == 0:
            interval = 0
            speed = 0
        else:
            # Calculate realistic time intervals
            traffic_factor = get_traffic_delay(current_time.hour, is_main_road)
            base_time = random.uniform(45, 120) if not is_main_road else random.uniform(40, 90)
            interval = int(base_time * traffic_factor)
            current_time += timedelta(seconds=interval)

            # Calculate speed between points
            time_diff = interval / 60.0
            prev_lat, prev_lng = journey_data[i - 1][0], journey_data[i - 1][1]
            speed = calculate_speed_between_points(prev_lat, prev_lng, lat, lng, time_diff)

            # Apply traffic conditions
            if 8 <= current_time.hour <= 10 or 18 <= current_time.hour <= 20:
                speed *= random.uniform(0.3, 0.6)  # Rush hour traffic
            elif is_main_road:
                speed *= random.uniform(0.7, 1.0)
            else:
                speed *= random.uniform(0.4, 0.8)

        # Battery drain simulation
        battery_drain = random.randint(0, 2) if i % 3 == 0 else 0
        battery_level = max(10, battery_level - battery_drain)

        # Collect data for bulk send
        timestamps.append(current_time.strftime("%Y-%m-%d %H:%M:%S"))
        latitudes.append(lat)
        longitudes.append(lng)
        batteries.append(battery_level)
        payloads.append({
            "temperature": round(random.uniform(25.0, 32.0), 2),
            "humidity": round(random.uniform(60.0, 80.0), 2),
            "speed": round(speed, 1)
        })

        print(f"  {i+1:2d}. {description[:50]:<50} | Speed: {speed:4.1f} km/h | Battery: {battery_level:2d}%")

    print(f"\n🚀 Sending all {len(timestamps)} points in one request...")

    # Send bulk data
    response = send_bulk_gps_data(DEVICE_ID, timestamps, latitudes, longitudes, batteries, payloads)

    # Summary
    print("\n" + "=" * 60)
    print("📊 BULK UPLOAD SUMMARY:")
    print(f"📍 Total Points: {len(timestamps)}")
    print(f"🕐 Journey Time: {start_time.strftime('%H:%M')} - {current_time.strftime('%H:%M')}")
    print(f"🔋 Final Battery: {battery_level}%")
    print("=" * 60)

def send_single_gps_data():
    """
    Send a single GPS data point manually with full response display
    """
    print("📍 Send Single GPS Data Point")
    print("-" * 40)

    try:
        # Get user input for GPS data
        lat = float(input("Enter Latitude: "))
        lng = float(input("Enter Longitude: "))
        speed = float(input("Enter Speed (km/h, or 0 if stationary): "))
        battery = int(input("Enter Battery Level (0-100): "))

        # Generate current timestamp
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n🚀 Sending GPS data...")
        print(f"📍 Location: {lat}, {lng}")
        print(f"🚗 Speed: {speed} km/h")
        print(f"🔋 Battery: {battery}%")
        print(f"🕐 Time: {timestamp}")
        print("-" * 60)

        # Send the data and display full response
        response = send_gps_data(DEVICE_ID, timestamp, lat, lng, battery, speed)

        print("-" * 60)
        if response:
            print("✅ Single data point sent successfully!")
        else:
            print("❌ Failed to send data")

    except ValueError:
        print("❌ Invalid input. Please enter valid numbers.")
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")

def run_realistic_journey_simulation():
    """
    Run individual GPS point simulation with delays and full response display
    """
    journey_data = get_journey_data()
    current_time = datetime.now().replace(hour=14, minute=30, second=0, microsecond=0)
    battery_level = 87

    print("=" * 100)
    print("🚗 REALISTIC GPS JOURNEY SIMULATION WITH RESPONSE DISPLAY")
    print("=" * 100)
    print(f"📍 Total Points: {len(journey_data)}")
    print(f"🕐 Start Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔋 Initial Battery: {battery_level}%")
    print("=" * 100)

    for i, (lat, lng, description, is_main_road) in enumerate(journey_data):

        if i == 0:
            timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
            speed = 0
            delay_seconds = 0
        else:
            # Calculate realistic delay
            traffic_factor = get_traffic_delay(current_time.hour, is_main_road)
            base_time = random.uniform(45, 120) if not is_main_road else random.uniform(40, 90)
            delay_seconds = int(base_time * traffic_factor)

            current_time += timedelta(seconds=delay_seconds)
            timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

            # Calculate speed
            time_diff = delay_seconds / 60.0
            prev_lat, prev_lng = journey_data[i - 1][0], journey_data[i - 1][1]
            speed = calculate_speed_between_points(prev_lat, prev_lng, lat, lng, time_diff)

            # Apply traffic conditions
            if 8 <= current_time.hour <= 10 or 18 <= current_time.hour <= 20:
                speed *= random.uniform(0.3, 0.6)

        # Battery drain
        battery_drain = random.randint(0, 2) if i % 3 == 0 else 0
        battery_level = max(10, battery_level - battery_drain)

        print(f"\n{i+1:2d}. {description}")
        print(f"    ⏱️  Delay: {delay_seconds:3d}s | 🚗 Speed: {speed:4.1f} km/h | 🔋 Battery: {battery_level:2d}%")
        print("    " + "-" * 80)

        # Send GPS data with full response display
        response = send_gps_data(DEVICE_ID, timestamp, lat, lng, battery_level, speed)

        # Short delay for demo
        time.sleep(1)

    print("\n" + "=" * 100)
    print("✅ REALISTIC JOURNEY SIMULATION COMPLETED!")
    print("=" * 100)

def main():
    """
    Main program entry point with user interface
    """
    print("🚗 Enhanced GPS Tracker Simulator with Response Display")
    print("=" * 65)
    print("Options:")
    print("1. Send single GPS data manually (with response display)")
    print("2. Run realistic journey simulation (individual points with responses)")
    print("3. Send all journey data at once (bulk upload with response)")

    choice = input("\nEnter your choice (1, 2, or 3): ").strip()

    if choice == "1":
        send_single_gps_data()
    elif choice == "2":
        print("\n🚀 Starting realistic journey simulation...")
        run_realistic_journey_simulation()
    elif choice == "3":
        send_bulk_journey_data()
    else:
        print("Invalid choice. Please run the program again and select 1, 2, or 3.")

# Run the program when executed directly
if __name__ == "__main__":
    main()
