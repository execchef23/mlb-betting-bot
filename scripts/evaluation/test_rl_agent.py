from betting_env import BettingEnv
from stable_baselines3 import PPO

# Load environment
env = BettingEnv()

# Load your trained agent
model = PPO.load("data/rl_betting_agent.zip")

# Run the agent
obs = env.reset()
done = False
total_reward = 0

while not done:
    action, _ = model.predict(obs)
    obs, reward, done, _ = env.step(action)
    total_reward += reward

print(f"\n🏁 Final Bankroll: ${env.bankroll:.2f}")
print(f"🎯 Total Reward: {total_reward:.2f}")