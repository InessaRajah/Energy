import gurobipy as gb
import numpy as np

agent = {'Index': 0, 'Type': 'Prosumer', 'AssetNum': 2, 'Assets': { 0: {'Type': 'Battery', 'a': 0.01, 'b': 0.02, 'ub' : 5, 'lb': -5}, 1: {'Type': 'Grid', 'a': 0.1, 'b': 0.2, 'ub' : 20, 'lb' : -20}}}
partners = np.array([2, 3])
preferences = [1, 1]
rho = 0.01

def createPlayers(agents, part, preferences, penalty_factor):
    players = np.zeros(len(agents))
    for i in range(len(agents)):
        p = Prosumer(agents[i], part, preferences, penalty_factor)
        players[i] = p
    return players

#class which can have objects set
class expando(object):
    pass


class Prosumer:
    def __init__(self, agent, partners, preferences, rho):
        self.data = expando()
        self.data.type = agent['Type']
        self.data.num_assets = agent['AssetNum']
        self.data.index = agent['Index']
        self.data.a = np.zeros([self.data.num_assets])
        self.data.b = np.zeros([self.data.num_assets])
        self.data.Pmin = np.zeros([self.data.num_assets])
        self.data.Pmax = np.zeros([self.data.num_assets])
        #returns the indices of the rows in part[index] that is nonzero i.e. the indices of trading partners
        self.data.partners = partners[self.data.index].nonzero()[0]
        self.data.num_partners = len(self.data.partners)
        print(self.data.num_partners)
        self.data.preferences = preferences
        self.data.rho = rho
        for i in range (self.data.num_assets):
            #agent is a nested dictionariy has inner dictionary Assets with another inner dictionariy cost-coff
            self.data.a[i] = agent['Assets'][i]['a']
            self.data.b[i] = agent['Assets'][i]['b']
            self.data.Pmax[i] = agent['Assets'][i]['ub']
            self.data.Pmin[i] = agent['Assets'][i]['lb']
            # Data -- Progress
        self.SW = 0
        self.Res_primal = 0
        self.Res_dual = 0
        
        # Model variables
        self.variables = expando()
        self.constraints = expando()
        self.results = expando()
        self._build_model()
        return

    def optimize(self, trade):
        self._iter_update(trade)
        self._update_objective()
        self.model.params.NonConvex = 2
        self.model.optimize()
        if self.model.solCount == 0:
            print("Model is infeasible")
            self.model.computeIIS()
            self.model.write("model_iis.ilp")
        self._opti_status(trade)
        trade[self.data.partners] = self.t_old
        return trade
    
    def production_consumption(self):
        prod = abs( np.array([self.variables.p[i].x for i in range(self.data.num_assets) if self.variables.p[i].x>0]).sum() )
        cons = abs( np.array([self.variables.p[i].x for i in range(self.data.num_assets) if self.variables.p[i].x<0]).sum() )
        return prod,cons

    ###
    #   Model Building
    ###
    def _build_model(self):
        self.model = gb.Model()
        self.model.setParam( 'OutputFlag', False )
        self._build_variables()
        self._build_constraints()
        self._build_objective()
        self.model.update()
        return

    def _build_variables(self):
        m = self.model
        self.variables.p = np.array([m.addVar(lb = self.data.Pmin[i], ub = self.data.Pmax[i], name = 'p') for i in range(self.data.num_assets)])
        self.variables.t = np.array([m.addVar(lb = -gb.GRB.INFINITY, name = 't') for i in range(self.data.num_partners)])
        self.variables.t_pos = np.array([m.addVar(name = 't_pos') for i in range(self.data.num_partners)]) #obj=self.data.pref[i], 
        self.t_old = np.zeros(self.data.num_partners)
        self.t_new = np.zeros(self.data.num_partners)
        self.y = np.zeros(self.data.num_partners)
        self.y0 = np.zeros(self.data.num_partners)
        m.update()
        return
        
    def _build_constraints(self):
        self.constraints.pow_bal = self.model.addConstr(sum(self.variables.p) == sum(self.variables.t))
        for i in range(self.data.num_partners):
            self.model.addConstr(self.variables.t[i] <= self.variables.t_pos[i])
            self.model.addConstr(self.variables.t[i] >= -self.variables.t_pos[i])
        return
        
    def _build_objective(self):
        self.obj_assets = (sum(self.data.b*self.variables.p + self.data.a*self.variables.p*self.variables.p/2) +
                           sum(self.data.preferences*self.variables.t_pos) ) 
        self.model.setObjective(self.obj_assets)
        self.model.update()
        return
    ###
    #   Model Updating
    ###    
    def _update_objective(self):
        y = np.asarray(self.y)
        t_average = np.asarray(self.t_average)
        augm_lag = (-sum(y*( self.variables.t - t_average )) + self.data.rho/2*sum( ( self.variables.t - t_average )*( self.variables.t - t_average )))
        #augm_lag = self.data.rho/2*sum((self.t_average - self.variables.t + self.y/self.data.rho)*(self.t_average - self.variables.t + self.y/self.data.rho))
        self.model.setObjective(self.obj_assets + augm_lag)
        self.model.update()
        return
        
    ###
    #   Iteration Update
    ###    
    def _iter_update(self, trade):
        self.t_average = (self.t_old - trade[self.data.partners])/2
        self.y = self.y - self.data.rho*(self.t_old - self.t_average)
        return
        
    ###
    #   Optimization status
    ###    
    def _opti_status(self,trade):
        for i in range(self.data.num_partners):
            self.t_new[i] = self.variables.t[i].x
        self.SW = -self.model.objVal
        self.Res_primal = sum( (self.t_new + trade[self.data.partners])*(self.t_new + trade[self.data.partners]) )
        self.Res_dual = sum( (self.t_new-self.t_old)*(self.t_new-self.t_old) )
        self.t_old = np.copy(self.t_new)
        return
    
    def Who(self):
        #print('Prosumer')
        self.who = 'Prosumer'
        return


