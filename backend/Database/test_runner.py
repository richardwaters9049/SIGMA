# File: /SIGMA/backend/Database/test_runner.py

from mission_store import insert_mission, fetch_all_missions

if __name__ == "__main__":
    # Test insert
    insert_mission("Trace Echo", difficulty="medium", is_active=True)
    insert_mission("Core Breach", difficulty="hard", is_active=False)
    insert_mission("Firewall Reboot", difficulty="easy", is_active=True)

    # Test fetch
    all_missions = fetch_all_missions()
    print("\n=== All Missions ===")
    for mission in all_missions:
        print(mission)
