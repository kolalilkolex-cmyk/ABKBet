"""
Crash Game Automation Script
Runs the crash game rounds automatically
"""
import requests
import time
import sys

BASE_URL = "http://127.0.0.1:5000"  # Change to your deployed URL

def run_crash_round():
    """Run one complete crash game round"""
    try:
        # Wait 5 seconds for betting phase
        print("⏰ Betting phase... (5 seconds)")
        time.sleep(5)
        
        # Start the game
        print("🚀 Starting game...")
        response = requests.post(f"{BASE_URL}/api/crash/start")
        if response.status_code == 200:
            data = response.json()
            print(f"✈️  Game #{data['game_id']} started! Crash point: {data['crash_point']}x")
        else:
            print(f"❌ Error starting game: {response.text}")
            return False
        
        # Let the game run (multiplier grows until crash point)
        # Average game duration: 5-15 seconds depending on crash point
        game_duration = min(data['crash_point'] * 2, 30)  # Max 30 seconds
        print(f"⏱️  Game running for ~{game_duration:.1f} seconds...")
        time.sleep(game_duration)
        
        # Reset for next round
        print("🔄 Resetting game...")
        response = requests.post(f"{BASE_URL}/api/crash/reset")
        if response.status_code == 200:
            print("✅ Game reset complete!\n")
        else:
            print(f"❌ Error resetting game: {response.text}\n")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in crash round: {e}\n")
        return False

def main():
    """Main loop to run crash game continuously"""
    print("🎮 ABKBet Crash Game Automation")
    print("=" * 50)
    print(f"🌐 Server: {BASE_URL}")
    print("⚡ Press Ctrl+C to stop\n")
    
    round_number = 1
    
    try:
        while True:
            print(f"🎲 Round #{round_number}")
            print("-" * 50)
            
            success = run_crash_round()
            
            if not success:
                print("⚠️  Round failed, retrying in 5 seconds...")
                time.sleep(5)
            
            round_number += 1
            time.sleep(2)  # Small pause between rounds
            
    except KeyboardInterrupt:
        print("\n\n🛑 Crash game automation stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
