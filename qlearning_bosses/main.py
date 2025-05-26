import argparse

from qlearning_bosses.Game import Game
from qlearning_bosses.agents.AgentWithCooldown import AgentWithCooldown
from qlearning_bosses.agents.BasicQLearningAgent import BasicQLearningAgent
from qlearning_bosses.agents.ConstrainedAngleAgent import ConstrainedAngleAgent
from qlearning_bosses.agents.RandomAgent import RandomAgent
from qlearning_bosses.targets.MovingTarget import MovingTarget
from qlearning_bosses.targets.MovingTargetWithRandom import MovingTargetWithRandom
from qlearning_bosses.targets.NaiveMovingTarget import NaiveMovingTarget
from qlearning_bosses.targets.StaticTarget import StaticTarget

AGENT_CLASSES = {
    "cooldown": AgentWithCooldown,
    "basic": BasicQLearningAgent,
    "constrained": ConstrainedAngleAgent,
    "random": RandomAgent,
}

TARGET_CLASSES = {
    "moving": MovingTarget,
    "naive": NaiveMovingTarget,
    "static": StaticTarget,
    "random": MovingTargetWithRandom,
}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=AGENT_CLASSES.keys(), default="basic", help="Type of agent to use")
    parser.add_argument("--target", choices=TARGET_CLASSES.keys(), default="moving", help="Type of target to use")
    parser.add_argument("--rounds", type=int, default=100, help="Time of simulation in rounds (positive integer)")
    parser.add_argument("--cooldown", type=float, default=0.01, help="Shot cooldown in seconds (float)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    agent_cls = AGENT_CLASSES[args.agent]
    target_cls = TARGET_CLASSES[args.target]
    game = Game(agent_cls=agent_cls, target_cls=target_cls, cooldown=float(args.cooldown))
    game.run(int(args.rounds))
