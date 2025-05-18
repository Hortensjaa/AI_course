# 🎯 Q-Learning Shooter: Aiming Agent Simulation

The main goal of this project is to simulate an agent learning how to hit a target using **Q-learning**.  
The simulation is built using **Pygame** and **PyBox2D**.  
The agent fires at various angles and updates its knowledge based on hits or misses, learning which angle works best for a given target position.

The project includes different agents with additional rules or constraints, as well as different types of targets.  
Simulation results can be found at the end of this file.

Approaches tested in this project and gathered data will be used to implement AI for bosses in
my other project - [Meowhalla](https://github.com/Hortensjaa/MeowHalla).

---
## 📦 Project Structure
```
mini_project/
├── agents/ # Folder containing agent implementations
│ ├── Agent.py # Base agent class
│ ├── RandomAgent.py # Agent acting randomly
│ ├── BasicQLearningAgent.py # Q-learning agent class
│ ├── AgentWithCooldown.py # Q-learning agent with extra constraint - cooldown and ability to pass move
│ ├── ConstrainedAngleAgent.py # Q-learning agent with extra constraint - can only shoot at certain angles based on last shot
├── targets/ # Folder containing target classes
│ ├── Target.py # Base target class
│ ├── StaticTarget.py # Not moving target
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
where:
- s - state in witch we selected the action
- a - action

---

### 🧠 Q-Learning Parameters

| Parameter   | Value          | Description                               |
|-------------|----------------|-------------------------------------------|
| α (alpha)   | 0.1            | Learning rate                             |
| γ (gamma)   | 0.99           | Discount factor for future rewards        |
| ε (epsilon) | 1.0 → 0.01     | Exploration vs exploitation (decaying)    |
| ε decay     | 0.999          | Slow decay                                |
| bin size    | 25 px          | State granularity (target X-position)     |
| reward      | $1 / (1 + d^2)$ | The closer the hit, the higher the reward |

---

## QLearning Agent With Cooldown
- Similar to basic Q-learning agent, but with an additional constraint: the agent can only shoot every $t$ ticks of waiting.
### 🔁 Q-Update Scheme:
> This version also uses simplified approach - agent has state now, but it doesn't matter in formula (I guess).

$$
Q[s][a] = Q[s][a] + \alpha \cdot (\text{reward} - Q[s][a])
$$

---

### 🧠 Q-Learning Parameters

| Parameter          | Value                                         | Description                                                        |
|--------------------|-----------------------------------------------|--------------------------------------------------------------------|
| α (alpha)          | 0.1                                           | Learning rate                                                      |
| γ (gamma)          | 0.99                                          | Discount factor for future rewards                                 |
| ε (epsilon)        | 1.0 → 0.001                                   | Exploration vs exploitation (decaying); smaller than for basic one |
| ε decay            | 0.995                                         | Faster decay                                                       |
| bin size           | 25 px                                         | State granularity (target X-position)                              |
| reward on hit      | $1$                                           | Big reward for hit                                                 |
| reward on miss     | $1 / (100 + d^2)$                             | The closer the hit, the higher the reward (but worse than wait)    |
| reward for waiting | $1 / (10 * max(t, ticks\_since\_last\_shot))$ | Little reward for waiting, but punish for waiting too long         |
| $t$                | $10$                                          | Cooldown value                                                     |

---

## QLearning Agent With Angle Constraint
- Similar to basic Q-learning agent, but with an additional constraint: the agent can only choose from angles,
that are adjacent to the last selected angle ($±(120/n)°$).
- Because of that, the last selected angle is stored in the state.
### 🔁 Q-Update Scheme:

$$
Q[s][a] = Q[s][a] + \alpha \cdot (\text{reward} + max(Q[s']) - Q[s][a])
$$
where $s'$ is the next state (the state after the action was taken).
---

### 🧠 Q-Learning Parameters

| Parameter          | Value           | Description                                |
|--------------------|-----------------|--------------------------------------------|
| α (alpha)          | 0.1             | Learning rate                              |
| γ (gamma)          | 0.99            | Discount factor for future rewards         |
| ε (epsilon)        | 1.0 → 0.02      | Exploration vs exploitation (decaying)     |
| ε decay            | 0.9999          | Slower decay, because of the states number |
| bin size           | 25 px           | State granularity (target X-position)      |
| reward      | $1 / (1 + d^2)$ | The closer the hit, the higher the reward  |

> Target size for testing this agent is 50% bigger, but set of angles and number of bins are reduced to avoid too big Q-table.

---

## ▶️ How to Run

1. Install required libraries:
   ```bash
   pip install pygame numpy
   ```

2. Run simulation:
   ```bash
    python3 -m qlearning_bosses.main --agent [basic|cooldown|constrained] --target [static|moving|random]
    ```
   
## 📊 Results
All agents were tested with moving targets. The "pass" is the hit rate >= 90%.

### Basic QLearning Agent
```
1. Hits: 176, Misses: 437, Success rate: 28.7%
2. Hits: 281, Misses: 215, Success rate: 56.7%
3. Hits: 467, Misses: 170, Success rate: 73.3%
4. Hits: 517, Misses: 146, Success rate: 78.0%
5. Hits: 433, Misses: 67, Success rate: 86.6%
6. Hits: 562, Misses: 63, Success rate: 89.9%
7. Hits: 588, Misses: 68, Success rate: 89.6%
8. Hits: 598, Misses: 60, Success rate: 90.9% <- PASSED
9. Hits: 437, Misses: 43, Success rate: 91.0% <- PASSED
10. Hits: 579, Misses: 55, Success rate: 91.3% <- PASSED
11. Hits: 607, Misses: 58, Success rate: 91.3% <- PASSED
12. Hits: 443, Misses: 43, Success rate: 91.2% <- PASSED
13. Hits: 575, Misses: 56, Success rate: 91.1% <- PASSED
14. Hits: 596, Misses: 59, Success rate: 91.0% <- PASSED
15. Hits: 601, Misses: 57, Success rate: 91.3% <- PASSED
16. Hits: 422, Misses: 38, Success rate: 91.7% <- PASSED
17. Hits: 598, Misses: 59, Success rate: 91.0% <- PASSED
18. Hits: 595, Misses: 64, Success rate: 90.3% <- PASSED
19. Hits: 429, Misses: 44, Success rate: 90.7% <- PASSED
20. Hits: 586, Misses: 54, Success rate: 91.6% <- PASSED
21. Hits: 600, Misses: 61, Success rate: 90.8% <- PASSED
22. Hits: 588, Misses: 57, Success rate: 91.2% <- PASSED
23. Hits: 436, Misses: 38, Success rate: 92.0% <- PASSED
24. Hits: 597, Misses: 59, Success rate: 91.0% <- PASSED
25. Hits: 587, Misses: 64, Success rate: 90.2% <- PASSED
26. Hits: 427, Misses: 39, Success rate: 91.6% <- PASSED
27. Hits: 599, Misses: 61, Success rate: 90.8% <- PASSED
28. Hits: 596, Misses: 61, Success rate: 90.7% <- PASSED
29. Hits: 572, Misses: 53, Success rate: 91.5% <- PASSED
30. Hits: 579, Misses: 57, Success rate: 91.0% <- PASSED
-----Total-----
Hits: 15671, Misses: 2406, Success rate: 86.7%
```
### QLearning Agent With Cooldown
This agent can easily learn to hit the target, because of the option to pass.
However, in some cases it can be stuck in local maximum for long, 
because of passing shot in uncertain states and then 
taking action in even worse situation, because of punishment for waiting too long.
On the other hand, it can also create the strategy of waiting a lot.
```
=== History - case 1 ===
1. Hits: 12, Misses: 28, Success rate: 30.0%
2. Hits: 26, Misses: 5, Success rate: 83.9%
3. Hits: 29, Misses: 0, Success rate: 100.0% <- PASSED
4. Hits: 22, Misses: 0, Success rate: 100.0% <- PASSED
5. Hits: 29, Misses: 1, Success rate: 96.7% <- PASSED
6. Hits: 34, Misses: 0, Success rate: 100.0% <- PASSED
7. Hits: 38, Misses: 0, Success rate: 100.0% <- PASSED
8. Hits: 30, Misses: 0, Success rate: 100.0% <- PASSED
9. Hits: 38, Misses: 0, Success rate: 100.0% <- PASSED
10. Hits: 36, Misses: 0, Success rate: 100.0% <- PASSED
11. Hits: 32, Misses: 0, Success rate: 100.0% <- PASSED
12. Hits: 38, Misses: 0, Success rate: 100.0% <- PASSED
13. Hits: 37, Misses: 1, Success rate: 97.4% <- PASSED
14. Hits: 36, Misses: 0, Success rate: 100.0% <- PASSED
15. Hits: 37, Misses: 0, Success rate: 100.0% <- PASSED
16. Hits: 37, Misses: 1, Success rate: 97.4% <- PASSED
17. Hits: 38, Misses: 0, Success rate: 100.0% <- PASSED
18. Hits: 29, Misses: 0, Success rate: 100.0% <- PASSED
19. Hits: 37, Misses: 0, Success rate: 100.0% <- PASSED
20. Hits: 38, Misses: 0, Success rate: 100.0% <- PASSED
-----Total-----
Hits: 653, Misses: 36, Success rate: 95.7%
===============

=== History - case 2 (bad balance in uncertain states) ===
1. Hits: 6, Misses: 38, Success rate: 13.6%
2. Hits: 11, Misses: 4, Success rate: 73.3%
3. Hits: 19, Misses: 3, Success rate: 86.4%
4. Hits: 20, Misses: 9, Success rate: 69.0%
5. Hits: 18, Misses: 11, Success rate: 62.1%
6. Hits: 15, Misses: 6, Success rate: 71.4%
7. Hits: 18, Misses: 10, Success rate: 64.3%
8. Hits: 22, Misses: 9, Success rate: 71.0%
9. Hits: 18, Misses: 8, Success rate: 69.2%
10. Hits: 23, Misses: 10, Success rate: 69.7%
11. Hits: 24, Misses: 10, Success rate: 70.6%
12. Hits: 23, Misses: 10, Success rate: 69.7%
13. Hits: 17, Misses: 9, Success rate: 65.4%
14. Hits: 24, Misses: 9, Success rate: 72.7%
15. Hits: 23, Misses: 11, Success rate: 67.6%
16. Hits: 17, Misses: 9, Success rate: 65.4%
17. Hits: 25, Misses: 8, Success rate: 75.8%
18. Hits: 23, Misses: 10, Success rate: 69.7%
19. Hits: 22, Misses: 10, Success rate: 68.8%
20. Hits: 25, Misses: 8, Success rate: 75.8%
-----Total-----
Hits: 393, Misses: 202, Success rate: 66.1%
===============


=== History - case 3 (passing very often) ===
1. Hits: 5, Misses: 33, Success rate: 13.2%
2. Hits: 13, Misses: 12, Success rate: 52.0%
3. Hits: 13, Misses: 1, Success rate: 92.9% <- PASSED
4. Hits: 12, Misses: 0, Success rate: 100.0% <- PASSED
5. Hits: 14, Misses: 1, Success rate: 93.3% <- PASSED
6. Hits: 15, Misses: 0, Success rate: 100.0% <- PASSED
7. Hits: 14, Misses: 1, Success rate: 93.3% <- PASSED
8. Hits: 10, Misses: 0, Success rate: 100.0% <- PASSED
9. Hits: 15, Misses: 0, Success rate: 100.0% <- PASSED
10. Hits: 10, Misses: 0, Success rate: 100.0% <- PASSED
-----Total-----
Hits: 136, Misses: 48, Success rate: 73.9%
```

### QLearning Agent With Angle Constraint
This agent needs more time to learn, because of more complex state.The learning curve makes it hard to go past 85%.
```
1. Hits: 167, Misses: 470, Success rate: 26.2% 
2. Hits: 119, Misses: 480, Success rate: 19.9% 
3. Hits: 212, Misses: 439, Success rate: 32.6% 
4. Hits: 219, Misses: 411, Success rate: 34.8% 
5. Hits: 258, Misses: 429, Success rate: 37.6% 
6. Hits: 179, Misses: 272, Success rate: 39.7% 
7. Hits: 257, Misses: 403, Success rate: 38.9% 
8. Hits: 304, Misses: 320, Success rate: 48.7% 
9. Hits: 238, Misses: 251, Success rate: 48.7% 
10. Hits: 335, Misses: 312, Success rate: 51.8% 
11. Hits: 362, Misses: 292, Success rate: 55.4% 
12. Hits: 327, Misses: 316, Success rate: 50.9% 
13. Hits: 258, Misses: 189, Success rate: 57.7% 
14. Hits: 394, Misses: 276, Success rate: 58.8% 
15. Hits: 384, Misses: 277, Success rate: 58.1% 
16. Hits: 297, Misses: 142, Success rate: 67.7% 
17. Hits: 396, Misses: 263, Success rate: 60.1% 
18. Hits: 435, Misses: 208, Success rate: 67.7% 
19. Hits: 481, Misses: 161, Success rate: 74.9% 
20. Hits: 333, Misses: 136, Success rate: 71.0% 
21. Hits: 453, Misses: 181, Success rate: 71.5% 
22. Hits: 453, Misses: 220, Success rate: 67.3% 
23. Hits: 354, Misses: 99, Success rate: 78.1% 
24. Hits: 445, Misses: 185, Success rate: 70.6% 
25. Hits: 456, Misses: 143, Success rate: 76.1% 
26. Hits: 417, Misses: 175, Success rate: 70.4% 
27. Hits: 461, Misses: 126, Success rate: 78.5% 
28. Hits: 520, Misses: 123, Success rate: 80.9% 
29. Hits: 494, Misses: 161, Success rate: 75.4% 
30. Hits: 410, Misses: 113, Success rate: 78.4% 
31. Hits: 459, Misses: 146, Success rate: 75.9% 
32. Hits: 511, Misses: 161, Success rate: 76.0% 
33. Hits: 459, Misses: 83, Success rate: 84.7% 
34. Hits: 521, Misses: 124, Success rate: 80.8% 
35. Hits: 533, Misses: 119, Success rate: 81.7% 
36. Hits: 484, Misses: 151, Success rate: 76.2% 
37. Hits: 407, Misses: 87, Success rate: 82.4% 
38. Hits: 490, Misses: 139, Success rate: 77.9% 
39. Hits: 549, Misses: 93, Success rate: 85.5% 
40. Hits: 468, Misses: 77, Success rate: 85.9% 
41. Hits: 557, Misses: 86, Success rate: 86.6% 
42. Hits: 550, Misses: 88, Success rate: 86.2% 
43. Hits: 499, Misses: 70, Success rate: 87.7% 
44. Hits: 555, Misses: 76, Success rate: 88.0% 
45. Hits: 540, Misses: 106, Success rate: 83.6% 
46. Hits: 555, Misses: 75, Success rate: 88.1% 
47. Hits: 446, Misses: 65, Success rate: 87.3% 
48. Hits: 569, Misses: 75, Success rate: 88.4% 
49. Hits: 555, Misses: 90, Success rate: 86.0% 
50. Hits: 442, Misses: 85, Success rate: 83.9% 
51. Hits: 569, Misses: 73, Success rate: 88.6% 
52. Hits: 569, Misses: 73, Success rate: 88.6% 
53. Hits: 551, Misses: 74, Success rate: 88.2% 
54. Hits: 436, Misses: 58, Success rate: 88.3% 
55. Hits: 580, Misses: 69, Success rate: 89.4% 
56. Hits: 575, Misses: 77, Success rate: 88.2% 
57. Hits: 434, Misses: 60, Success rate: 87.9% 
58. Hits: 573, Misses: 73, Success rate: 88.7% 
59. Hits: 571, Misses: 74, Success rate: 88.5% 
60. Hits: 504, Misses: 64, Success rate: 88.7% 
61. Hits: 561, Misses: 68, Success rate: 89.2% 
62. Hits: 589, Misses: 65, Success rate: 90.1% <- PASSED
63. Hits: 569, Misses: 69, Success rate: 89.2% 
64. Hits: 439, Misses: 52, Success rate: 89.4% 
65. Hits: 578, Misses: 63, Success rate: 90.2% <- PASSED
66. Hits: 581, Misses: 80, Success rate: 87.9% 
67. Hits: 446, Misses: 50, Success rate: 89.9% 
68. Hits: 577, Misses: 70, Success rate: 89.2% 
69. Hits: 574, Misses: 64, Success rate: 90.0% 
70. Hits: 547, Misses: 90, Success rate: 85.9% 
71. Hits: 445, Misses: 53, Success rate: 89.4% 
72. Hits: 565, Misses: 63, Success rate: 90.0% 
73. Hits: 570, Misses: 71, Success rate: 88.9% 
74. Hits: 426, Misses: 80, Success rate: 84.2% 
75. Hits: 578, Misses: 71, Success rate: 89.1% 
76. Hits: 584, Misses: 68, Success rate: 89.6% 
77. Hits: 542, Misses: 64, Success rate: 89.4% 
78. Hits: 579, Misses: 62, Success rate: 90.3% <- PASSED
79. Hits: 573, Misses: 66, Success rate: 89.7% 
80. Hits: 562, Misses: 68, Success rate: 89.2% 
81. Hits: 447, Misses: 50, Success rate: 89.9% 
82. Hits: 560, Misses: 94, Success rate: 85.6% 
83. Hits: 578, Misses: 73, Success rate: 88.8% 
84. Hits: 447, Misses: 53, Success rate: 89.4% 
85. Hits: 573, Misses: 62, Success rate: 90.2% <- PASSED
86. Hits: 563, Misses: 71, Success rate: 88.8% 
87. Hits: 565, Misses: 69, Success rate: 89.1% 
88. Hits: 448, Misses: 51, Success rate: 89.8% 
89. Hits: 577, Misses: 64, Success rate: 90.0% <- PASSED
90. Hits: 573, Misses: 67, Success rate: 89.5% 
91. Hits: 438, Misses: 49, Success rate: 89.9% 
92. Hits: 569, Misses: 73, Success rate: 88.6% 
93. Hits: 581, Misses: 70, Success rate: 89.2% 
94. Hits: 532, Misses: 64, Success rate: 89.3% 
95. Hits: 571, Misses: 76, Success rate: 88.3% 
96. Hits: 535, Misses: 91, Success rate: 85.5% 
97. Hits: 571, Misses: 60, Success rate: 90.5% <- PASSED
98. Hits: 446, Misses: 53, Success rate: 89.4% 
99. Hits: 543, Misses: 91, Success rate: 85.6% 
100. Hits: 570, Misses: 63, Success rate: 90.0% <- PASSED
-----Total-----
Hits: 47501, Misses: 12945, Success rate: 78.6%
```