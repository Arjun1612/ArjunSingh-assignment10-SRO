import docker
import time
import requests
import random
import logging
from datetime import datetime

class ChaosEngineer:
    def __init__(self):
        self.client = docker.from_env()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def kill_random_container(self, service_pattern="lab10"):
        """Kill a random container matching the pattern"""
        containers = self.client.containers.list(filters={"name": service_pattern})
        if not containers:
            self.logger.warning("No containers found matching pattern")
            return False
        target = random.choice(containers)
        self.logger.info(f"Killing container: {target.name}")
        try:
            target.kill()
            return True
        except Exception as e:
            self.logger.error(f"Failed to kill container: {e}")
            return False

    def network_partition(self, container_name, duration=30):
        """Simulate network partition by stopping/starting container"""
        try:
            container = self.client.containers.get(container_name)
            self.logger.info(f"Stopping {container_name} for {duration}s")
            container.stop()
            time.sleep(duration)
            container.start()
            self.logger.info(f"Restarted {container_name}")
            return True
        except Exception as e:
            self.logger.error(f"Network partition failed: {e}")
            return False

    def cpu_stress(self, container_name, duration=60):
        """Apply CPU stress to container"""
        try:
            container = self.client.containers.get(container_name)
            # Execute stress command inside container
            stress_cmd = f"timeout {duration} stress --cpu 1"
            result = container.exec_run(stress_cmd, detach=True)
            self.logger.info(f"Applied CPU stress to {container_name}")
            return True
        except Exception as e:
            self.logger.error(f"CPU stress failed: {e}")
            return False

    def monitor_system_health(self, duration=30, interval=5):
        """Monitor system health during chaos experiments"""
        start_time = time.time()
        health_data = []
        while time.time() - start_time < duration:
            try:
                # Check API health
                response = requests.get('http://localhost:5000/health', timeout=2)
                api_health = response.status_code == 200
            except:
                api_health = False
            try:
                # Check web service
                response = requests.get('http://localhost:8080', timeout=2)
                web_health = response.status_code == 200
            except:
                web_health = False
            health_record = {
                'timestamp': datetime.now().isoformat(),
                'api_health': api_health,
                'web_health': web_health
            }
            health_data.append(health_record)
            self.logger.info(f"Health check: API={api_health}, Web={web_health}")
            time.sleep(interval)
        return health_data

def run_chaos_experiment():
    chaos = ChaosEngineer()
    print("Starting Chaos Engineering Experiment")
    print("=" * 50)
    # Start monitoring
    print("Starting health monitoring...")
    # Run different chaos experiments
    experiments = [
        ("Container Kill", lambda: chaos.kill_random_container()),
        ("Network Partition", lambda: chaos.network_partition("lab10-chaos-engineering_api_1", 30)),
        ("CPU Stress", lambda: chaos.cpu_stress("lab10-chaos-engineering_api_1", 60))
    ]
    for exp_name, exp_func in experiments:
        print(f"\nRunning experiment: {exp_name}")
        success = exp_func()
        if success:
            print(f"{exp_name} executed successfully")
            # Monitor for 60 seconds after each experiment
            health_data = chaos.monitor_system_health(60, 5)
            # Calculate availability
            total_checks = len(health_data)
            healthy_checks = sum(1 for h in health_data if h["api_health"])
            availability = (healthy_checks / total_checks) * 100 if total_checks > 0 else 0
            print(f"System availability: {availability:.1f}%")
        else:
            print(f"{exp_name} failed to execute")
        time.sleep(10)

if __name__ == '__main__':
    run_chaos_experiment()