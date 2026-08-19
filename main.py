from scripts.ingest import fetch_local_rail_trails

def main():
    rail_trails = fetch_local_rail_trails()
    print('Rail Trails Loaded.')
    
if __name__ == '__main__':
    main()