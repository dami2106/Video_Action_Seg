import gym
from gym import spaces
import numpy as np
from random import randint, shuffle
from PIL import Image
from collections import deque


class ColorsEnv(gym.Env):
    def __init__(self, env_name):
        super(ColorsEnv, self).__init__()
        self.SIZE = 5
        self.WORLD = np.zeros((self.SIZE, self.SIZE))

        self.COLORS = {
            1 : (0,   0,   0  ),
            2 : (255, 0,   0  ),
            3 : (0,   255, 0  ),
            4 : (0,   0,   255),
        }

        self.setup_world()

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high = 5, shape=(self.SIZE, self.SIZE), dtype=int)

        self.state_dim = 11
        self.action_dim = 5
        self.env_type = 'colours'

        self.has_red = False
        self.has_green = False
        self.has_blue = False


    def setup_world(self):
        self.WORLD = np.zeros((self.SIZE, self.SIZE))

        randomised_everything = True

        if randomised_everything:
            coordinates = set()
            while len(coordinates) < 4:
                x = randint(*(0, self.SIZE - 1))
                y = randint(*(0, self.SIZE - 1))
                coordinates.add((x, y))
            coordinates = list(coordinates)

        else:
            coordinates = []    
            coordinates.append((0, 2))
            coordinates.append((4, 4))
            coordinates.append((2, 1))
            shuffle(coordinates)
            while True:
                x = randint(*(0, self.SIZE - 1))
                y = randint(*(0, self.SIZE - 1))
                if (x, y) not in coordinates:
                    coordinates.append((x, y))
                    break
        
            coordinates.reverse()


        print("coords", coordinates)

        objects = [1, 2, 3, 4]

        for s, coord in zip(objects, coordinates):
            self.WORLD[coord[0], coord[1]] =  s


    def reset(self):
        self.setup_world()
        self.has_red = False
        self.has_green = False
        self.has_blue = False
        return self.WORLD
        
    def get_char_pos(self, dir):
        #row col 
        directions = {
            0 : np.array([-1,  0]),  #UP
            1 : np.array([1 ,  0]),  #DOWN
            3 : np.array([0 ,  1]),  #RIGHT
            2 : np.array([0 , -1])   #LEFT
        }

        char_pos = np.array([np.where(self.WORLD == 1)[0][0], np.where(self.WORLD == 1)[1][0]])
        new_char_pos = char_pos + directions[dir]

        for i in range(2):
            if new_char_pos[i] < 0 or new_char_pos[i] >= self.SIZE:
                return char_pos
        return new_char_pos

    def move_char(self, dir):
        old_ = np.array([np.where(self.WORLD == 1)[0][0], np.where(self.WORLD == 1)[1][0]])
        new_ = self.get_char_pos(dir)
        
        self.WORLD[old_[0], old_[1]] = 0
        self.WORLD[new_[0], new_[1]] = 1

    def step(self, action):
        self.move_char(action)
        state = self.WORLD
        simple_state = get_simple_obs(state)
    
        done = (2 not in state) and (3 not in state) and (4 not in state)

        if (self.has_red == False) and (simple_state[4] == 1):
            self.has_red = True
            reward = 1 
        elif (self.has_green == False) and (simple_state[7] == 1):
            self.has_green = True
            reward = 1 
        elif (self.has_blue == False) and (simple_state[10] == 1):
            self.has_blue = True
            reward = 1 
        else:
            reward = -0.5
    

        return state, reward, done, {} 

    def render(self, mode='human'):        
        print(self.get_obs())

            
    def close(self):
        pass

def get_img_from_obs(obs):
    color_map = {
        2: (255, 0, 0),   #RED
        3: (0, 255, 0),   #GREEN
        4: (0, 0, 255),   #BLUE
        
        1: (0, 0, 0),   #CHAR
        0: (255, 255, 255),   #WHITE BG

    }
    image_data = np.zeros((obs.shape[0], obs.shape[1], 3), dtype=np.uint8)  
    for i in range(obs.shape[0]):
        for j in range(obs.shape[1]):
            image_data[i, j] = color_map[obs[i, j]]
    image = Image.fromarray(image_data, 'RGB')
    # image_resized = image.resize((64, 64), Image.NEAREST)
    return image

def find_shortest_path(grid, goal_nb):
    # Define directions
    directions = {
        0: np.array([-1, 0]),  # UP
        1: np.array([1, 0]),   # DOWN
        2: np.array([0, -1]),  # LEFT
        3: np.array([0, 1])    # RIGHT
    }
    
    dir_map = {
        (0, 1): 3,  # RIGHT
        (1, 0): 1,  # DOWN
        (0, -1): 2, # LEFT
        (-1, 0): 0  # UP
    }
    
    rows, cols = len(grid), len(grid[0])
    
    start = None
    end = None
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                start = (r, c)
            elif grid[r][c] == goal_nb:
                end = (r, c)
    
    if not start or not end:
        return []

    queue = deque([(start[0], start[1], [])])  # (row, col, path)
    visited = set()
    visited.add(start)
    
    while queue:
        r, c, path = queue.popleft()
        
        if (r, c) == end:
            return path
        
        for dr, dc in directions.values():
            nr, nc = r + dr, c + dc
            
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                if grid[nr][nc] == 0 or grid[nr][nc] == goal_nb:  # Avoid obstacles
                    visited.add((nr, nc))
                    new_dir = dir_map[(dr, dc)]
                    queue.append((nr, nc, path + [new_dir]))
    
    return []



def find_colour_index(list, index):
    for i, l in enumerate(list):
        if l[index] == 1:
            return i

    

def add_in_pickup(obs_list:list, action_list:list):
    updated_obs = obs_list.copy()
    updated_acts = action_list.copy()
    colour_ind = {
        'red' : find_colour_index(obs_list, 4),
        'green' : find_colour_index(obs_list, 7),
        'blue' : find_colour_index(obs_list, 10)
    }

    colour_places = {
        'red' :   4,
        'green' : 7,
        'blue' :  10
    }

    #Sort it in ascending order 
    colour_ind = dict(sorted(colour_ind.items(), key=lambda item: item[1]))

    for i, col in enumerate(colour_ind):
        row_old = updated_obs[colour_ind[col] + i].copy()
        row_old[colour_places[col]] = 0
        updated_obs.insert((colour_ind[col] + i), row_old)

        updated_acts.insert(colour_ind[col] + i, 4)

    return updated_obs, updated_acts


def get_3d_obs(obs, size=5):
    new_obs = np.zeros((4, size, size), dtype=np.uint8)

    has_red = 2 in obs
    has_green = 3 in obs 
    has_blue = 4 in obs 

    agent = get_coords(obs, 1)  # Assuming this returns a single coordinate [x, y]
    reds = get_coords(obs, 2, multiple=True) if has_red else []  # Assuming it can return multiple coordinates
    green = get_coords(obs, 3) if has_green else [-1, -1]
    blue = get_coords(obs, 4) if has_blue else [-1, -1]

    new_obs[0, agent[0], agent[1]] = 1  # Mark agent's position
    
    print(reds)

    # Mark all red objects in the corresponding channel
    for red in reds:
        new_obs[1, red[0], red[1]] = 1

    new_obs[2, green[0], green[1]] = 1 if has_green else 0  # Green object
    new_obs[3, blue[0], blue[1]] = 1 if has_blue else 0  # Blue object

    return new_obs

    
# def get_coords(obs, search):
#     pos = np.where(obs == search)   
#     return [pos[0][0], pos[1][0]]

def get_coords(obs, target, multiple=False):
    coords = np.argwhere(obs == target)
    if multiple:
        return [list(coord) for coord in coords]  # Return all coordinates
    return list(coords[0]) if len(coords) > 0 else [-1, -1]  # Return first occurrence

def get_simple_obs(obs):
    # [agent_x, agent_y, dis_r_x, dis_r_y, has_red, dis_g_x,\\
    #  dis_g_y, has_green, dis_b_x, dis_r_x, has_blue ] 

    has_red = 2 in obs
    has_green = 3 in obs 
    has_blue = 4 in obs 

    agent = get_coords(obs, 1)
    red = get_coords(obs, 2) if has_red else [-1, -1]
    green = get_coords(obs, 3) if has_green else [-1, -1]
    blue = get_coords(obs, 4) if has_blue else [-1, -1]

    state = np.zeros(11)

    state[0] = agent[0] #agent x 
    state[1] = agent[1] #agent y 

    state[2] = agent[0] - red[0] if has_red else 0  #distance red x 
    state[3] = agent[1] - red[1] if has_red else 0 #distance red y 
    state[4] = 0 if has_red else 1 #If have red in state

    state[5] = agent[0] - green[0] if has_green else 0  #distance green x 
    state[6] = agent[1] - green[1] if has_green else 0  #distance green y 
    state[7] = 0 if has_green else 1 #If have green in state

    state[8] = agent[0] - blue[0] if has_blue else 0  #distance blue x 
    state[9] = agent[1] - blue[1] if has_blue else 0  #distance blue y 
    state[10] = 0 if has_blue else 1 #If have blue in state

    return state


def run_episode(env, goals = [2, 3, 4]):
    obs = env.reset()
    shuffle(goals) #Randomise order of colours 
    done = False 
    # ep_states = [get_3d_obs(obs.copy()).flatten()] 
    # ep_states = [obs.copy().flatten()]
    ep_states = [get_simple_obs(obs.copy())]
    ep_actions = []
    ep_rewards = []
    ground_truth = []
    ep_length = 0

    truth_mapping = {
        2 : 'red',
        3 : 'green',
        4 : 'blue'
    }

    for goal in goals:
        path = find_shortest_path(obs, goal)
   
        for action in path: 
            obs, reward, done, _ = env.step(action)
            # ep_states.append(obs.copy().flatten())
            # ep_states.append(get_3d_obs(obs.copy()).flatten())
            ep_states.append(get_simple_obs(obs.copy()))
            ep_actions.append(action)
            ep_rewards.append(reward)
            ground_truth.append(truth_mapping[goal])
            ep_length += 1

  

    ep_actions.append(-1)



    # ep_states, ep_actions = add_in_pickup(ep_states, ep_actions)

    # ep_length = len(ep_states[:-1])

    return ep_states[:-1], ep_actions[:-1], ep_rewards, ep_length, done, ground_truth


"""
A function to create an Nx3 numpy array of the colours that the agent is looking for at each time step
@param state_set: The states of the trace
@return: An Nx3 numpy array of the colours the agent is looking for at each time step
"""
def extract_looking_for(state_set):
    colours = []
    for state in state_set:
        colours.append((state[4], state[7], state[10]))
    colours.append((1, 1, 1))
    return colours


"""
A function to determine the objectives of the agent at each time step
@param state_set: The states of the trace
@return: A list of the colours the agent is looking for at each time step
"""
def determine_objectives(state_set):
    trace = extract_looking_for(state_set)
   
    ind = [ 
        [0, "red"],
        [0, "green"],
        [0 , "blue"]
    ]

    for i in range(len(trace)):
        if trace[i][0] == 1:
            ind[0][0] = i
            break
    for i in range(len(trace)):
        if trace[i][1] == 1:
            ind[1][0] = i
            break    
    for i in range(len(trace)):
        if trace[i][2] == 1:
            ind[2][0] = i
            break      

    ind = sorted(ind, key=lambda x: x[0])
    
    first = (0, ind[0][0])
    second = (ind[0][0], ind[1][0])
    third = (ind[1][0], len(trace) - 1)
    colours = []

    for i in range(first[0], first[1]):
        colours.append(ind[0][1])
    for i in range(second[0], second[1]):
        colours.append(ind[1][1])
    for i in range(third[0], third[1]):
        colours.append(ind[2][1])

    return colours

def save_colours_demonstrations(nb_traces = 100, max_steps = 12):
    env = ColorsEnv('colours')
    tn = 0 
    
    while tn < nb_traces:
        try: 
            states, actions, _, length, done, ground_truth = run_episode(env)


            if done and length == 12 :
                
                #Convert actions to one-hot encoding
                actions = np.array(actions)
                actions = np.eye(4)[actions]
                states = np.array(states)
                # states = np.concatenate((states, actions), axis=1)
                print(states.shape)
         
                np.save(f'data/desktop_assembly/features/{tn}_colours', states)
                
                #Save the groundtruth as a text file with each string on a new line
                with open(f'data/desktop_assembly/groundTruth/{tn}_colours', 'w') as f:
                    for item in ground_truth:
                        f.write("%s\n" % item)

                tn += 1
        except:
            print("Error")
            pass


if __name__ == '__main__':
    env = ColorsEnv('colours')

    save_colours_demonstrations(100, 12)
    # states, actions, _, length, done, ground_truth = run_episode(env)

    # for s in states:
    #     print(s.reshape(5, 5))
    #     print()

#    