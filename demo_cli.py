#!/usr/bin/env python3
"""
Crisis Commander Demo CLI
Interactive command-line interface for demonstrating the Crisis Commander system
"""

import asyncio
import json
import sys
import time
import requests
import websocket
from datetime import datetime
from threading import Thread
from typing import Dict, Any


class CrisisCommanderDemo:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.ws = None
        self.incidents = []
        
    def display_banner(self):
        """Display the Crisis Commander banner"""
        print("\n" + "="*70)
        print("🚨  DevOps CRISIS COMMANDER  🚨")
        print("Multi-Agent Incident Response System")
        print("AgentHack 2025 Winner Project")
        print("="*70 + "\n")
    
    def display_system_status(self):
        """Display current system status"""
        try:
            response = requests.get(f"{self.base_url}/demo/status")
            if response.status_code == 200:
                status = response.json()
                print("📊 SYSTEM STATUS:")
                print(f"   ✅ Mode: {status['mode']}")
                print(f"   🤖 Agents Available: {status['agents_available']}")
                print(f"   🎭 Scenarios Available: {status['scenarios_available']}")
                print(f"   🔗 WebSocket Connections: {status['websocket_connections']}")
                print()
            else:
                print("❌ Could not connect to Crisis Commander API")
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    def list_scenarios(self):
        """List available simulation scenarios"""
        try:
            response = requests.get(f"{self.base_url}/scenarios")
            if response.status_code == 200:
                scenarios = response.json()
                print("🎭 AVAILABLE INCIDENT SCENARIOS:")
                print("-" * 50)
                for i, (key, scenario) in enumerate(scenarios.items(), 1):
                    severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(scenario['severity'], "⚪")
                    print(f"{i:2d}. {severity_icon} {scenario['name']}")
                    print(f"     💭 {scenario['description']}")
                    print(f"     🏗️  Affects: {', '.join(scenario['affected_services'])}")
                    print()
                return scenarios
            else:
                print("❌ Could not fetch scenarios")
                return {}
        except Exception as e:
            print(f"❌ Error fetching scenarios: {e}")
            return {}
    
    def simulate_incident(self, scenario_name: str):
        """Simulate an incident"""
        print(f"🚨 SIMULATING INCIDENT: {scenario_name}")
        print("⏳ Initiating multi-agent response workflow...")
        
        try:
            response = requests.post(
                f"{self.base_url}/incidents/simulate",
                json={"scenario_name": scenario_name},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                incident_id = result['incident_id']
                print(f"✅ Incident Created: {incident_id}")
                print(f"📊 Status: {result['status']}")
                
                # Wait for processing and show timeline
                time.sleep(3)
                self.show_incident_details(incident_id)
                
                return incident_id
            else:
                print(f"❌ Simulation failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error during simulation: {e}")
            return None
    
    def show_incident_details(self, incident_id: str):
        """Show detailed incident information"""
        try:
            response = requests.get(f"{self.base_url}/incidents/{incident_id}")
            if response.status_code == 200:
                incident = response.json()
                print("\n" + "="*60)
                print("📋 INCIDENT DETAILS")
                print("="*60)
                print(f"ID: {incident['incident_id']}")
                print(f"Status: {incident['status']}")
                print(f"Created: {incident['created_at']}")
                
                if incident.get('classification'):
                    cls = incident['classification']
                    print(f"\n🔍 CLASSIFICATION:")
                    print(f"   Category: {cls['category']}")
                    print(f"   Severity: {cls['severity']}")
                    print(f"   Confidence: {cls['confidence']:.1%}")
                    print(f"   Tags: {', '.join(cls['tags'])}")
                
                print(f"\n⏱️  TIMELINE ({len(incident['timeline'])} events):")
                for i, event in enumerate(incident['timeline'], 1):
                    agent_icon = {"IncidentClassifier": "🔍", "ResolutionAdvisor": "🛠️", "PostMortemGenerator": "📝"}.get(event['agent'], "🤖")
                    print(f"   {i}. {agent_icon} {event['agent']}: {event['action']}")
                    print(f"      ⏱️ {event['timestamp']} ({event['duration_ms']}ms)")
                
                print("="*60 + "\n")
            else:
                print(f"❌ Could not fetch incident details: {response.status_code}")
        except Exception as e:
            print(f"❌ Error fetching incident details: {e}")
    
    def interactive_demo(self):
        """Run interactive demo mode"""
        self.display_banner()
        self.display_system_status()
        
        while True:
            print("🎮 DEMO OPTIONS:")
            print("1. 📋 List Available Scenarios")
            print("2. 🚨 Simulate Random Incident")
            print("3. 🎯 Simulate Specific Incident")
            print("4. 📊 Show System Status")
            print("5. 📈 Show Active/Completed Incidents")
            print("6. 🔄 Reset System")
            print("0. 🚪 Exit")
            
            try:
                choice = input("\nSelect option (0-6): ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    self.list_scenarios()
                elif choice == "2":
                    print("🎲 Simulating random incident...")
                    self.simulate_incident(None)  # Random scenario
                elif choice == "3":
                    scenarios = self.list_scenarios()
                    if scenarios:
                        scenario_list = list(scenarios.keys())
                        try:
                            idx = int(input(f"Enter scenario number (1-{len(scenario_list)}): ")) - 1
                            if 0 <= idx < len(scenario_list):
                                scenario_name = scenario_list[idx]
                                self.simulate_incident(scenario_name)
                            else:
                                print("❌ Invalid scenario number")
                        except ValueError:
                            print("❌ Please enter a valid number")
                elif choice == "4":
                    self.display_system_status()
                elif choice == "5":
                    self.show_incident_summary()
                elif choice == "6":
                    self.reset_system()
                else:
                    print("❌ Invalid option. Please try again.")
                    
                input("\\nPress Enter to continue...")
                print("\\n" + "-"*70 + "\\n")
                
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_incident_summary(self):
        """Show summary of all incidents"""
        try:
            active_resp = requests.get(f"{self.base_url}/incidents/active")
            completed_resp = requests.get(f"{self.base_url}/incidents/completed")
            
            if active_resp.status_code == 200 and completed_resp.status_code == 200:
                active = active_resp.json()
                completed = completed_resp.json()
                
                print("📊 INCIDENT SUMMARY:")
                print(f"   🔴 Active Incidents: {len(active)}")
                print(f"   ✅ Completed Incidents: {len(completed)}")
                print(f"   📈 Total Processed: {len(active) + len(completed)}")
                
                if completed:
                    print("\\n✅ RECENT COMPLETED INCIDENTS:")
                    for incident in completed[-5:]:  # Show last 5
                        print(f"   • {incident['incident_id'][:8]}... ({incident['status']})")
            else:
                print("❌ Could not fetch incident summary")
        except Exception as e:
            print(f"❌ Error fetching summary: {e}")
    
    def reset_system(self):
        """Reset the system"""
        try:
            response = requests.post(f"{self.base_url}/admin/reset")
            if response.status_code == 200:
                print("🔄 System reset successfully!")
            else:
                print("❌ Could not reset system")
        except Exception as e:
            print(f"❌ Error resetting system: {e}")


def main():
    """Main demo function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Auto demo mode
        demo = CrisisCommanderDemo()
        demo.display_banner()
        demo.display_system_status()
        
        scenarios = demo.list_scenarios()
        if scenarios:
            # Simulate a few incidents automatically
            scenario_names = list(scenarios.keys())[:3]
            for scenario in scenario_names:
                print(f"\\n🎭 Auto-simulating: {scenario}")
                demo.simulate_incident(scenario)
                time.sleep(2)
        
        demo.show_incident_summary()
    else:
        # Interactive demo mode
        demo = CrisisCommanderDemo()
        demo.interactive_demo()


if __name__ == "__main__":
    main()