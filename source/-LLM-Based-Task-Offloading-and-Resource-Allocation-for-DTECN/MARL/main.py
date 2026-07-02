from marl_train import Runner, Agent
from setting import arg
import env

if __name__ == '__main__':
    # get the params
    args = arg()
    my_env = env.Environment(args.lane_num, args.n_agents, args.task_num)
    runner = Runner(args, my_env)
    if args.evaluate:
        pass
    else:
        runner.run() 
        