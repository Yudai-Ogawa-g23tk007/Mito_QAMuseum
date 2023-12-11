# 複数回最適化によるサブツアー排除
from ctypes import c_int32
from amplify import gen_symbols, BinaryPoly,Solver, decode_solution, BinaryQuadraticModel, sum_poly,BinarySymbolGenerator
from amplify.client import FixstarsClient
import numpy as np
from .omuradata import data,time_for_move_calc,time_stay
import math
def qa_stsp(T, start, speed_move, speed_watch, must_visit, already_vist, subroute,N,ts,sat,tm):
    subroute_len = 0
    for i in range(len(subroute)):
        if len(subroute[i]) > subroute_len:
            subroute_len = len(subroute[i])

    x = gen_symbols(BinaryPoly, N*N+subroute_len*len(subroute)) 
    waiting_time = [0]*N
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

    time_const = (1+0.10)*(sum_poly(N, lambda i: sum_poly(N, lambda j: tm[i][j]*speed_move*x[i*N+j]))**2 + 2*sum_poly(N, lambda i: sum_poly(N, lambda j: tm[i][j]*speed_move*x[i*N+j]))*sum_poly(N, lambda i: (ts[i]*speed_watch+waiting_time[i])*sum_poly(N, lambda j: x[i*N+j])) + sum_poly(N, lambda i: (ts[i]*speed_watch+waiting_time[i])*sum_poly(N, lambda j: x[i*N+j]))**2) - 2*(sum_poly(N, lambda i: sum_poly(N, lambda j: tm[i][j]*speed_move*x[i*N+j])) + sum_poly(N, lambda i: (ts[i]*speed_watch+waiting_time[i])*sum_poly(N, lambda j: x[i*N+j])))*((1-0.10)*T+0.10)
    
    once_visit_const = sum_poly(N, lambda i: sum_poly(N, lambda j: x[j*N+i])*(sum_poly(N, lambda j: x[j*N+i])-1))
    
    once_route_const = sum_poly(N-1, lambda i: sum_poly(i+1,N, lambda j: x[i*N+j]*x[j*N+i]))
    print(subroute)
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
    
    #c3_param = abs(BinaryQuadraticModel(time_const).logical_matrix[0].to_numpy()).max()
    #p = 40
    maxtm=0.15*60
    maxts=6.0
    tmts=(maxtm+maxts)*(maxtm+maxts)
    if T<=30:
        c3_param=2.2*tmts
    else:
        c3_param=2*(maxtm+maxts)*T-tmts+0.1*(2*(maxtm+maxts)*(T-1)-tmts)
    if T <= 5:
        p = 40
    elif T <= 10:
        p = 15
    elif T <= 20:
        p = 10
    else:
        p = 4
    print(p)
    # T = 60 p = 9
    # T = 70 p = 9
    model = BinaryQuadraticModel(cost + vertex_const*p + sg_const*p + time_const/c3_param*p + once_visit_const*p + once_route_const*p + subtour_const*p + already_vist_const*p + must_visit_const*p)  ### いい感じにPTしたい ###
    
    # Fixstars Amplify
    client = FixstarsClient()
   #client.token = "mwve4EyfjZgVTuENPRDQc9cdTgxhWPxP"
    client.token="4rCqRgV5trByWr7BDlTgTFu8GMznfGUy"
    client.parameters.timeout = 1

    solver = Solver(client)
    result = solver.solve(model)
    values = result[0].values
    energy = result[0].energy
    print(energy)
    x_values = decode_solution(x, values, 1)
    answer = np.where(np.array(x_values) == 1)[0]
    
    if qa_stsp_judge(answer, start, already_vist, must_visit, subroute, subroute_len,N):
        path, route_time, sub = qa_stsp_decode(answer, start, speed_move, speed_watch, subroute,N,tm,ts)
        print(path)
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
        subtour_const = sum((sum(sum(x[subroute[i][j]*N+subroute[i][k]] for k in range(len(subroute[i]))) for j in range(len(subroute[i])))-sum(x[N*N+subroute_len*i+l] for l in range(len(subroute[i])-1)))**2 for i in range(len(subroute)))
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
    print(dp)
    flag = True
    path = []
    s = 0
    i = start
    sub = []
    while len(dp)!=0:
        if not flag and sub == []:
            s = dp[0][0]
            sub.append(s)
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
                subroute.append(sub)
                sub = []
    
    if flag:
        route_time = 0
        for p in range(1,len(path)):
            route_time += tm[path[p-1]][path[p]]*60/speed_move
            route_time += ts[path[p]]*speed_watch
        route_time -= ts[0]*speed_watch
        return path, route_time, subroute
    else:
        return [], 0, subroute

def calculatepath(T,tt,br):
    print(tt)
    N, tm, ts, sat = data()
    
    speed_move=60*60/tt
    
    path=[]
    start=0
    
    
    speed_watch=1.0/br
    
    must_visit=[]
    already_visit=[]
    flag = False
    #subroute=[]
    subroute = [[1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6], [5, 6, 7], [6, 7, 8], [7, 8, 9], [8, 9, 10], [9, 10, 11], [10, 11, 12], [11, 12, 13], [12, 13, 14], [13, 14, 15], [14, 15, 16], [15, 16, 17], [16, 17, 18], [17, 18, 19]]
    re_opt=-1
    while path==[] and re_opt < 20:
        path, goal_time, subroute = qa_stsp(T, start, speed_move, speed_watch, must_visit, already_visit, subroute,N,ts,sat,tm)
        re_opt += 1
        print("re_opt:",re_opt)
    print(T)
    print(path)
    return path


def recalculate(T,speed_move,speed_watch,visit_spot,now_spot):
    N,tm,ts,sat = data()
    path=[]
    must_visit=[]
    print("T",T,"speed",speed_move,"watach",speed_watch,"visit",visit_spot)
    #tm=time_for_move_calc(speed_move)
    #ts=time_stay(speed_watch)
    #subroute=[]
    subroute = [[1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6], [5, 6, 7], [6, 7, 8], [7, 8, 9], [8, 9, 10], [9, 10, 11], [10, 11, 12], [11, 12, 13], [12, 13, 14], [13, 14, 15], [14, 15, 16], [15, 16, 17], [16, 17, 18], [17, 18, 19]]
    re_opt=-1

    while path==[] and re_opt < 10:
        path, goal_time, subroute=qa_stsp(T, now_spot, speed_move, speed_watch, must_visit, visit_spot, subroute,N,ts,sat,tm)
        re_opt+=1

    
    return path

def find_path(start,already_vist,N,tm):
    gen = BinarySymbolGenerator()
    x = gen.array(N, N)

    cost = sum_poly(N-1, lambda n: sum_poly(N-1, lambda i: sum_poly(N-1, lambda j: tm[i+1][j+1]*x[n][i]*x[n+1][j]))) + sum_poly(N-1, lambda i: tm[start][i+1]*x[0][i] + tm[i+1][0]*x[N-1][i]) # 移動時間の最小化
    const1 = sum_poly(N, lambda n: (sum_poly(N, lambda i: x[n][i]) - 1)**2)  # 全ての地点を通る
    const2 = sum_poly(N, lambda i: (sum_poly(N, lambda n: x[n][i]) - 1)**2)  # 同時に1地点だけ通る

    if already_vist != []:
        already_vist_const = sum_poly(1, len(already_vist), lambda i: sum_poly(N, lambda j: x[j*N+already_vist[i]]))
    else:
        already_vist_const = 0
    p=50
    consts = const1 + const2+already_vist_const
    model = BinaryQuadraticModel(cost + consts*p)

    # Amplify AE
    client = FixstarsClient()
    client.token = "4rCqRgV5trByWr7BDlTgTFu8GMznfGUy"
    client.parameters.timeout = 1000

    solver = Solver(client)
    result = solver.solve(model)
    energy, values = result[0].energy, result[0].values
    cr = solver.client_result
    at = cr.annealing_time_ms
    x_values = x.decode(values)
    path = np.where(np.array(x_values) == 1)[1]
    
    path.appendleft(start)
    path.append(0)

    return path, energy, at

def TSPCalculate():
    N,tm,ts,sat = data()
    path=[]
    already_visit=[]
    start = 0
    N -= 1
    re_opt = -1
    while path == [] and re_opt < 10:
        path,energy,at = find_path(start,already_visit,N,tm)
        re_opt += 1
    
    return path

def GoalTime(path,speed_move,speed_watch):
    
    N,tm,ts,sat = data()
    route_time = 0
    for p in range(1,len(path)):
        route_time += tm[int(path[p-1])][int(path[p])]*60/speed_move
        route_time += ts[int(path[p])]*speed_watch
    route_time -= ts[0]*speed_watch
    
    return route_time