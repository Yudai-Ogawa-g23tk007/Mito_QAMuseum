# 複数回最適化によるサブツアー排除
from ctypes import c_int32
from amplify import gen_symbols, BinaryPoly,Solver, decode_solution, BinaryQuadraticModel, sum_poly
from amplify.client import FixstarsClient
import numpy as np
from .omuradata import data,time_for_move_calc,time_stay

def qa_stsp(T, start, speed_move, speed_watch, must_visit, already_vist, subroute,N,tm,ts,sat):
    subroute_len = 0
    waiting_time=[0]*N
    for i in range(len(subroute)):
        if len(subroute[i]) > subroute_len:
            subroute_len = len(subroute[i])

    x = gen_symbols(BinaryPoly, N*N+subroute_len*len(subroute)) 

    vertex_const = 0
    for i in range(N):
        if i != 0 and i != start:
            out = 0
            for j in range(N):
                if i != j:
                    out += x[j*N+i]
            vertex_const += (sum_poly(N, lambda j: x[i*N+j])-out)**2

    start_const = 0
    goal_const = 0
    for j in range(N):
        if start != j:
            start_const += x[start*N+j]
        if 0 != j:
            goal_const += x[j*N+0]
    sg_const = (start_const-1)**2 + (goal_const-1)**2

    time_const = (1+0.1)*(sum_poly(N, lambda i: sum_poly(N, lambda j: tm[i][j]*speed_move*x[i*N+j]))**2 + 2*sum_poly(N, lambda i: sum_poly(N, lambda j: tm[i][j]*speed_move*x[i*N+j]))*sum_poly(N, lambda i: (ts[i]*speed_watch+waiting_time[i])*sum_poly(N, lambda j: x[i*N+j])) + sum_poly(N, lambda i: (ts[i]*speed_watch+waiting_time[i])*sum_poly(N, lambda j: x[i*N+j]))**2) - 2*(sum_poly(N, lambda i: sum_poly(N, lambda j: tm[i][j]*speed_move*x[i*N+j])) + sum_poly(N, lambda i: (ts[i]*speed_watch+waiting_time[i])*sum_poly(N, lambda j: x[i*N+j])))*((1-0.1)*T+0.1)
    
    once_visit_const = sum_poly(N, lambda i: sum_poly(N, lambda j: x[j*N+i])*(sum_poly(N, lambda j: x[j*N+i])-1))
    
    once_route_const = sum_poly(N-1, lambda i: sum_poly(i+1,N, lambda j: x[i*N+j]*x[j*N+i]))
    
    if subroute != []:
        subtour_const = sum_poly(len(subroute), lambda i: (sum_poly(len(subroute[i]), lambda j: sum_poly(len(subroute[i]), lambda k: x[subroute[i][j]*N+subroute[i][k]]))-sum_poly(len(subroute[i])-1, lambda l: x[N*N+subroute_len*i+l]))**2)
    else:
        subtour_const = 0

    if already_vist != []:
        already_vist_const = sum_poly(1, len(already_vist), lambda i: sum_poly(N, lambda j: x[j*N+already_vist[i]]))
    else:
        already_vist_const = 0

    if must_visit != []:
        must_visit_const = sum_poly(must_visit, lambda i: (sum_poly(N, lambda j: x[j*N+i]) - 1)**2)  ### 絶対に訪問したい地点を通る制約関数 ###
    else:
        must_visit_const = 0
        
    cost = -sum_poly(N, lambda i: sat[i]*sum_poly(N, lambda j: x[i*N+j]))
    
    c3_param = abs(BinaryQuadraticModel(time_const).logical_matrix[0].to_numpy()).max()
    
    model = BinaryQuadraticModel(cost + vertex_const*20000 + sg_const*20000 + time_const/c3_param*10000 + once_visit_const*10000 + once_route_const*10000 + subtour_const*10000 + already_vist_const*20000 + must_visit_const*10000)  ### いい感じにPTしたい ###
    
    # Fixstars Amplify
    client = FixstarsClient()
    #client.token = "mwve4EyfjZgVTuENPRDQc9cdTgxhWPxP"
    client.token="4rCqRgV5trByWr7BDlTgTFu8GMznfGUy"
    client.parameters.timeout = 1000

    solver = Solver(client)
    result = solver.solve(model)
    values = result[0].values
    x_values = decode_solution(x, values, 1)
    answer = np.where(np.array(x_values) == 1)[0]
    
    if qa_stsp_judge(answer, start, already_vist, must_visit, subroute, subroute_len,N):
        path, route_time, sub = qa_stsp_decode(answer, start, speed_move, speed_watch, subroute,N,tm,ts)
    else:
        path, route_time, sub = [], 0, subroute

    return  path, route_time, sub


def qa_stsp_judge(answer, start, already_vist, must_visit, subroute, subroute_len,N):
    x = [0]*(N*N+subroute_len*len(subroute)) 
    for i in answer:
        x[i] = 1
    
    vertex_const = 0
    for i in range(N):
        if i != 0 and i != start:
            out = 0
            for j in range(N):
                if i != j:
                    out += x[j*N+i]
            vertex_const += (sum(x[i*N+j] for j in range(N))-out)**2

    start_const = 0
    goal_const = 0
    for j in range(N):
        if start != j:
            start_const += x[start*N+j]
        if 0 != j:
            goal_const += x[j*N+0]
            
    sg_const = (start_const-1)**2 + (goal_const-1)**2
    once_visit_const = sum(sum(x[j*N+i] for j in range(N))*(sum(x[j*N+i] for j in range(N))-1) for i in range(N))
    once_route_const = sum(sum(x[i*N+j]*x[j*N+i] for j in range(i+1,N)) for i in range(N))
    
    if subroute != []:
        subtour_const = sum((sum(x[subroute[i][j]*N+subroute[i][k]] for k in range(len(subroute[i]))) for j in range(sum_poly(len(subroute[i])))-sum(x[N*N+subroute_len*i+l] for l in range(len(subroute[i])-1)))**2 for i in range(len(subroute)))
    else:
        subtour_const = 0

    if already_vist != []:
        already_vist_const = sum(sum(x[j*N+already_vist[i]] for j in range(N)) for i in range(1,len(already_vist)))
    else:
        already_vist_const = 0

    if must_visit != []:
        must_visit_const = sum((sum(x[j*N+i] for j in range(N)) - 1)**2 for i in must_visit)
    else:
        must_visit_const = 0

    #print(vertex_const, sg_const, once_visit_const, once_route_const, subtour_const, already_vist_const)
    if vertex_const != 0 or sg_const != 0 or once_visit_const != 0 or once_route_const != 0 or subtour_const != 0 or already_vist_const != 0 or must_visit_const != 0:
        return False 

    return True


def qa_stsp_decode(answer, start, speed_move, speed_watch, subroute,N,tm,ts):
    dp = []
    for p in answer:
        if p >= N*N:
            break
        i = int(p / N)
        j = p % N
        dp.append((i,j))
    flag = True
    path = []
    s = 0
    i = start
    sub = []
    while len(dp)!=0:
        if not flag and sub == []:
            sub.append(dp[0][0])
            i = dp[0][1]
            dp.remove(dp[0])

        for p in dp:
            if p[0] == i:
                if flag:
                    path.append(i)
                else:
                    sub.append(i)
                i = p[1]
                dp.remove(p)
                break
            if p == dp[len(dp)-1]:
                return [], False, subroute

        if i == s:
            if flag:
                path.append(i)
                if dp != []:
                    flag = False
            else:
                sub.append(i) 
                subroute.append(sub)
                sub = []
    
    if flag:
        route_time = 0
        for p in range(1,len(path)):
            route_time += tm[path[p-1]][path[p]]*speed_move
            route_time += ts[path[p]]*speed_watch
        route_time -= ts[0]*speed_watch
        return path, route_time, subroute
    else:
        return [], 0, subroute
    

def recalculate(T,speed_move,speed_watch,visit_spot,now_spot):
    N,spot,stay,sat = data()
    path=[]
    must_visit=[]
    tm=time_for_move_calc(speed_move)
    ts=time_stay(speed_watch)
    subroute=[]
    re_opt=-1

    while path==[] and re_opt < 10:
        path, goal_time, subroute=qa_stsp(T, now_spot, speed_move, speed_watch, must_visit, visit_spot, subroute,N,tm,ts,sat)
        re_opt+=1

    
    return path




"""
if __name__ == "__main__":
    ### 美術館データの読み込み ###
    N, tm, ts, sat = data()

    ### ユーザパラメータ ###
    T = 20             # int: 総滞在時間
    speed_move = 60    # int: 歩行速度
    speed_watch = 1.0  # int: 閲覧時間
    must_visit = []    # list: 絶対に訪れたい地点
    already_vist = []  # list: 既に訪れた地点

    path = []          # list: 巡回経路
    goal_time = 0      # int: 終了予定時刻
    now_spot = 0       # int: 現在地点
    start_time = 0     # int?time?: 移動開始時刻
    est_time = 1       # int?time?: 移動完了予定時刻
    real_time = 2      # int?time?: 移動完了時刻

    ### その他 ###
    TIME = 0           # int?time?: 現在時刻
    waiting_time = [0]*N  # list: 待ち時間

    subroute = []
    opt_count = 0
    while path == [] and opt_count < 10:
        path, goal_time, subroute = qa_stsp(T, now_spot, speed_move, speed_watch, must_visit, already_vist, subroute)
        opt_count += 1
    if opt_count == 10:
        raise RuntimeError("Break infinite loops.")
    print(path, goal_time)

    if est_time != real_time:
        subroute = []
        opt_count = 0

        already_vist = [0,1,7]
        now_spot = 7
        path = []
        while path == [] and opt_count < 10:
            path, goal_time, subroute = qa_stsp(T-(TIME-start_time), now_spot, speed_move, speed_watch, must_visit, already_vist, subroute)
            opt_count += 1
        if opt_count == 10:
            raise RuntimeError("Break infinite loops.")
        print(path, goal_time)
        """