# 🎯 Q-Learning Shooter: Aiming Agent Simulation

The main goal of this project is to simulate an agent learning how to hit a target using **Q-learning**.  
The simulation is built using **Pygame** and **PyBox2D**.  
The agent fires at various angles and updates its knowledge based on hits or misses, learning which angle works best for a given target position.

The project includes different agents with additional rules or constraints, as well as different types of targets.  
Simulation results can be found at the end of this file.

---
## 📦 Project Structure
```
mini_project/
├── agents/ # Folder containing agent implementations
│ ├── Agent.py # Base agent class
│ ├── RandomAgent.py # Agent acting randomly
│ ├── BasicQLearningAgent.py # Q-learning agent class
│ ├── QLearningAgentWithCooldown.py # Q-learning agent with extra constraint - cooldown and ability to pass move
├── targets/ # Folder containing target classes
│ ├── Target.py # Base target class
│ ├── MovingTarget.py # Target moving steadily from wall to wall
│ ├── MovingTargetWithRandom.py # Target with small probability of sudden direction change
├── Bullet.py # Bullet class with physics logic
├── Main.py # Main game loop and simulation controller
├── constants.py # Global constants (screen size, PPM, etc.)
```
---

## Basic QLearning Agent

- The agent observes the target's X position, which is discretized into bins (every 25 pixels).
- The agent can choose from a set of discrete shooting angles (from -60° to 60°).
- It learns using Q-learning — it starts by exploring randomly (`epsilon = 1.0`) and gradually shifts toward exploiting better actions (`epsilon` decays to `0.01`).
- After each shot, the agent receives a reward and updates its Q-table.

### 🔁 Q-Update Scheme:
> This version uses a simplified approach – the agent is stateless and always has access to the same set of actions.

$$
Q[s][a] = Q[s][a] + \alpha \cdot (\text{reward} - Q[s][a])
$$

---

## 🧠 Q-Learning Parameters

| Parameter     | Value           | Description                                  |
|---------------|-----------------|----------------------------------------------|
| α (alpha)     | 0.1             | Learning rate                                |
| γ (gamma)     | 0.99            | Discount factor for future rewards           |
| ε (epsilon)   | 1.0 → 0.01      | Exploration vs exploitation (decaying)       |
| bin size      | 25 px           | State granularity (target X-position)        |
| reward        | $1 / (1 + d^2)$ | The closer the hit, the higher the reward |

---

## ▶️ How to Run

1. Install required libraries:
   ```bash
   pip install pygame numpy
   ```

2. Run simulation:
   ```bash
    python Main.py
    ```
   
## 📊 Results
```
Todo!
```