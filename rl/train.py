import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from rl.memory import ReplayMemory, Transition
from rl.dqn import DQN

from itertools import count

BATCH_SIZE = 128
GAMMA = 0.999
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 200
TARGET_UPDATE = 10

policy_net = DQN()
target_net = DQN()
target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

optimizer = optim.RMSprop(policy_net.parameters())
memory = ReplayMemory(10000)

steps_done = 0

episode_durations = []

def optimize_model():
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)

    batch = Transition(*zip(*transitions))

    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), dtype=torch.uint8)
    non_final_next_states = torch.cat([s for s in batch.next_state
                                       if s is not None])
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    argument_batch = torch.cat(batch.argument)
    reward_batch = torch.cat(batch.reward)

    act, arg = policy_net(state_batch)

    state_action_values = act#.gather(1, action_batch)
    state_argument_values = act#.gather(1, argument_batch)

    next_state_values = torch.zeros(BATCH_SIZE)

    n_act, n_arg = target_net(non_final_next_states)
    next_state_values[non_final_mask] = n_act.max(1)[0].detach()

    expected_state_action_values = (next_state_values * GAMMA) + reward_batch
    expected_state_argument_values = (next_state_values * GAMMA) + reward_batch

    loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1)) + F.smooth_l1_loss(state_argument_values, expected_state_argument_values.unsqueeze(1))

    optimizer.zero_grad()
    loss.backward()
    for param in policy_net.parameters():
        param.grad.data.clamp_(-1, 1)
    optimizer.step()

def runner():
    num_episodes = 50
    for i_episode in range(num_episodes):
        # Initialize the environment and state
        last_screen = torch.randn([1,32*32*5+1])
        current_screen = torch.randn([1,32*32*5+1])
        state = current_screen - last_screen
        for t in count():
            # Select and perform an action
            # action = select_action(state)
            # _, reward, done, _ = env.step(action.item())
            action = torch.tensor([[0.,1.,0.]])
            argument = torch.tensor([[0.,1.,0.,0.]])
            done = ((i_episode+1)%400 == 0)
            reward = torch.tensor([[5.]])

            # Observe new state
            last_screen = current_screen
            current_screen = torch.randn([1,32*32*5+1])
            if not done:
                next_state = current_screen - last_screen
            else:
                next_state = None

            # Store the transition in memory
            memory.push(state, action,argument, next_state, reward)

            # Move to the next state
            state = next_state

            # Perform one step of the optimization (on the target network)
            optimize_model()
            if done:
                episode_durations.append(t + 1)
                break
        # Update the target network
        if i_episode % TARGET_UPDATE == 0:
            target_net.load_state_dict(policy_net.state_dict())

    print('Complete')

runner()