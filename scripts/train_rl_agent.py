import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from betting_env import BettingEnv
from stable_baselines3 import PPO

# Initialize environment
env = BettingEnv()

# Create PPO agent
model = PPO("MlpPolicy", env, verbose=1)

# Train
model.learn(total_timesteps=10000)

# Save
model.save("data/rl_betting_agent.zip")
print("✅ RL Agent trained and saved.")