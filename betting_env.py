import gym
import numpy as np
import pandas as pd
from gym import spaces

class BettingEnv(gym.Env):
    def __init__(self, data_path="data/live_game_features.csv"):
        super(BettingEnv, self).__init__()

        # Load features
        self.df = pd.read_csv(data_path)
        import xgboost as xgb

        # Load your trained model
        model = xgb.XGBClassifier()
        model.load_model("data/xgb_model_smart.json")

        # Encode teams like you did during training
        team_map = {team: code for code, team in enumerate(
            pd.concat([self.df["home_team"], self.df["away_team"]]).unique()
        )}
        self.df["home_team_code"] = self.df["home_team"].map(team_map)
        self.df["away_team_code"] = self.df["away_team"].map(team_map)

        # Match features used in training
        self.df["run_diff"] = self.df["home_avg_run_diff"] - self.df["away_avg_run_diff"]

        model_input = self.df[["home_team_code", "away_team_code", "home_avg_run_diff", "run_diff"]]
        probs = model.predict_proba(model_input)[:, 1]  # Home win probs

        self.df["model_home_win_prob"] = probs
        self.df["edge"] = self.df["model_home_win_prob"] - 0.5  # Baseline implied edge
        self.df["edge"] = self.df["model_home_win_prob"] - 0.5  # Simulated edge

        self.current_step = 0
        self.bankroll = 1000.0
        self.initial_bankroll = 1000.0

        # Observation: [model_prob, edge]
        self.observation_space = spaces.Box(low=0, high=1, shape=(2,), dtype=np.float32)

        # Action: 0 = no bet, 1 = small bet, 2 = med, 3 = big
        self.action_space = spaces.Discrete(4)

    def _get_obs(self):
        row = self.df.iloc[self.current_step]
        return np.array([row["model_home_win_prob"], row["edge"]], dtype=np.float32)

    def step(self, action):
        row = self.df.iloc[self.current_step]
        prob = row["model_home_win_prob"]
        odds = 1.9  # Simplified payout
        edge = row["edge"]

        bet_sizes = [0, 10, 25, 50]
        bet = bet_sizes[action]

        # Simulate game outcome
        win = np.random.rand() < prob

        reward = 0
        if bet > 0:
            if win:
                reward = bet * (odds - 1)
                self.bankroll += reward
            else:
                reward = -bet
                self.bankroll -= bet

        self.current_step += 1
        done = self.current_step >= len(self.df)

        obs = self._get_obs() if not done else np.array([0, 0])
        return obs, reward, done, {}

    def reset(self):
        self.current_step = 0
        self.bankroll = self.initial_bankroll
        return self._get_obs()