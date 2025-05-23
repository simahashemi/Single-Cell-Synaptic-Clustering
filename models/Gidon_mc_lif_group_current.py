# -*- coding: utf-8 -*-
"""TODO"""

import numpy as np

import core.core_global as core
from core.core_definitions import simulation_timestep
from core.mc_neuron_group import McNeuronGroup


class McLifGroup(McNeuronGroup):
    """TODO"""

    def __init__(self, size, num_branches, params={}):
        """TODO"""
        print('Gidon_dendrites')
        super().__init__(size, num_branches)

        core.kernel.register_spiking_group(self)

        if self.evolve_locally:
            self.branch = self.Branch((num_branches, self.rank_size), self,
                                      params.get("branch_parameters", {}))
            self.soma = self.Soma(self.rank_size, self.branch, self,
                                  params.get("soma_parameters", {}))

    def evolve(self):
        """TODO"""
        self.branch.evolve()
        self.soma.evolve()

    @staticmethod
    def spike_condition(mem, slope, v_thr, c1=0.4, c2=0.5):
        """TODO"""
        if slope > 0:
            spike_probability = np.clip(c1 * np.exp(c2 * (mem - v_thr)), 0, 1)
            return core.kernel.rng.binomial(1, spike_probability)
        else:
            return 0

    class Soma:
        """TODO"""

        def __init__(self, size, branch, nrn, params={}):
            """TODO"""
            self.size = size
            self.branch = branch
            self.nrn = nrn

            self.v_thr = params.get("v_thr", -55.0)
            print('Soma thr:', self.v_thr)
            self.v_rest = params.get("v_rest", -70.0)
            self.r_l = params.get("r_l", 4.0)
            self.r_mem = params.get("r_mem", 40e6)
            self.c_mem = params.get("c_mem", 250e-12)
            self.tau_mem = self.r_mem * self.c_mem
            self.tau_syn = params.get("tau_syn", 2e-3)
            self.set_refractory_period(params.get("refractory_period", 5e-3))

            self.mem = np.full(size, self.v_rest)
            self.ref = np.zeros(size, dtype=np.int)
            self.syn_current = np.zeros(size)
            self.br_current = np.zeros(size)

            self._tmp = np.zeros(size)
            self._last_mem = np.zeros(size)
            self._slope_mem = np.zeros(size)

            self.calculate_scale_constants()

        def rank2global(self, i):
            """TODO"""
            return self.nrn.rank2global(i)

        def get_post_size(self):
            """TODO"""
            return self.nrn.get_post_size()

        def calculate_scale_constants(self):
            """TODO"""
            self.scale_mem = simulation_timestep / self.tau_mem
            self.scale_syn = np.exp(-simulation_timestep / self.tau_syn)

        def set_refractory_period(self, t):
            """TODO"""
            self.refractory_period = t / simulation_timestep

        def evolve(self):
            """TODO"""
            self.integrate_synapses()
            self.compute_branch_current()
            self.integrate_membrane()
            self.check_thresholds()

        def integrate_synapses(self):
            """TODO"""
            np.multiply(self.syn_current, self.scale_syn, self.syn_current)

        def compute_branch_current(self):
            """TODO"""
            np.add.reduce(np.multiply(1 / self.r_l, np.maximum(0, np.subtract(
                self.branch.mem, self.mem))), out=self.br_current)

        def integrate_membrane(self):
            """TODO"""
            np.copyto(self._last_mem, self.mem)
            np.subtract(self.v_rest, self.mem, self._tmp)
            np.add(self._tmp, self.br_current, self._tmp)
            np.add(self._tmp, self.syn_current, self._tmp)
            np.add(np.multiply(self.scale_mem, self._tmp, self._tmp),
                   self.mem, self.mem)
            np.subtract(self.mem, self._last_mem, self._slope_mem)

        def check_thresholds(self):
            """TODO"""
            for i in range(self.size):
                if self.ref[i] == 0:
                    if McLifGroup.spike_condition(self.mem[i],
                                                  self._slope_mem[i],
                                                  self.v_thr):
                        self.nrn.push_spike(i)
#                         print("Soma Spike")
                        self.mem[i] = self.v_rest
                        self.ref[i] = self.refractory_period
                else:
                    self.mem[i] = self.v_rest
                    self.ref[i] -= 1
          

    class Branch:
        """TODO"""

        def __init__(self, size, nrn, params={}):
            """TODO"""
            self.size = size
            self.nrn = nrn

            self.v_thr = params.get("v_thr", -55.0)
            self.v_rest = params.get("v_rest", -70.0)
            self.r_mem = params.get("r_mem", 40e6)
            self.c_mem = params.get("c_mem", 250e-12)
            self.tau_mem = self.r_mem * self.c_mem
            self.tau_syn = params.get("tau_syn", 2e-3)
            self.tau_sod = params.get("tau_sod", 4e-3)
            self.a_sod_max = params.get("a_sod_max", 5.0)
            self.v_pla = params.get("v_pla", -30.0)
            self.I_amp = params.get("I_amp", 3.0)

############Gidon_Manuscript
            self.graded = params.get("graded", True )
            print("Graded: ",self.graded)
            self.tau_dCaAP = params.get("tau_dCaAP", 0.3 )
            self.thr_dCaAP = params.get("thr_dCaAP", -36.0 )
            print('dendrite thr:', self.thr_dCaAP)

            self.ref_dCaAP = params.get("ref_dCaAP", 200e-3)
            self.tau_A = params.get("tau_A", 3e-3)
            self.tau_B = params.get("tau_B", 4e-4)
            self.dCaAP_delta_t = params.get("dCaAP_delta_t", 21e-3)
            self.max_dCaAp_amp = 0
            self.w_dCaAP = params.get("w_dCaAP", 1.6 * 50 ) 
            self.A_init = 0.001
            self.B_init = 0
            self.A_dCaAP = np.full(self.size, self.A_init)
            self.B_dCaAP = np.full(self.size, self.B_init)
            self.thr_mem_v = np.zeros(self.size)
            self.I_dCaAP = np.zeros(self.size)
            self.ref_time = np.zeros(self.size)
            self.spike_step_counter = np.zeros(self.size)
            self.mem_prime = np.zeros(self.size)

################

            self.scale_pla = params.get("scale_pla", 140e-3)
            self.plateau_duration_min = params.get("plateau_duration_min",
                                                   0e-3)
            self.plateau_duration_max = params.get("plateau_duration_max",
                                                   300e-3)
            self.branch_dynamics = params.get("branch_dynamics",True)


            self.mem = np.full(self.size, self.v_rest)
            self.pla = np.zeros(self.size, dtype=np.int)
            self.pla_on = np.zeros(self.size, dtype=np.int)
            self.syn_current = np.zeros(self.size)

            self._tmp = np.zeros(self.size)
            self._a_sod = np.zeros(self.size)
            self._last_mem = np.zeros(self.size)
            self._slope_mem = np.zeros(self.size)
            self._tmp_current = np.zeros(self.size)
            self._current = np.zeros(self.size)

            self.calculate_scale_constants()

            if self.branch_dynamics:
                self.threshold_function = self.check_thresholds
            else:
                self.threshold_function = self.check_thresholds2
               

        def rank2global(self, i):
            """TODO"""
            return self.nrn.rank2global(i)

        def get_post_size(self):
            """TODO"""
            return self.nrn.get_post_size()

        def calculate_scale_constants(self):
            """TODO"""
            self.scale_mem = simulation_timestep / self.tau_mem
            self.mul_syn = simulation_timestep / self.tau_syn
            self.scale_syn = np.exp(-simulation_timestep / self.tau_syn)
            self.scale_sod = np.exp(-simulation_timestep / self.tau_sod)


        def evolve(self):
            """TODO"""
            
            self.integrate_synapses()
            self.integrate_membrane_pre()
            self.threshold_function()
            self.integrate_membrane_post()



        def integrate_synapses(self):
            """TODO"""
            np.multiply(self.syn_current, self.scale_syn, self.syn_current)
            np.add(np.multiply(np.subtract(self.syn_current, self._tmp_current),self.mul_syn),
                   self._tmp_current, self._tmp_current)
#             np.multiply(np.e, self._tmp_current, self._current)
            np.multiply(self.I_amp * np.e, self._tmp_current, self._current)
                
                
                
            

        def integrate_membrane_pre(self):
            """TODO"""
            np.copyto(self.mem_prime, self.mem)
            np.subtract(self.v_rest, self.mem_prime, self._tmp)
            np.add(self._tmp, self._current, self._tmp)
            np.add(np.multiply(self.scale_mem, self._tmp, self._tmp),self.mem_prime, self.mem_prime)
            
        def integrate_membrane_post(self):
            """TODO"""
            np.copyto(self._last_mem, self.mem)
            np.subtract(self.v_rest, self.mem, self._tmp)
            np.add(self._tmp, self._current, self._tmp)
            np.add(self._tmp, self.I_dCaAP, self._tmp)
            np.add(np.multiply(self.scale_mem, self._tmp, self._tmp),self.mem, self.mem)
            np.subtract(self.mem, self._last_mem, self._slope_mem)
        
            
            
            
###################################################################################################


        def dCaAP(self,j,i):
            if self.graded == False:
                self.max_dCaAp_amp = 1.0
            else:
                self.max_dCaAp_amp = np.exp(-(self.thr_mem_v[j,i]-self.thr_dCaAP)/((self.thr_dCaAP-self.v_rest)*self.tau_dCaAP))
            self.A_dCaAP[j,i] = 1/(1+np.exp(-(self.spike_step_counter[j,i]/self.tau_A)))
            self.B_dCaAP[j,i] = 1/(1+np.exp(-(self.spike_step_counter[j,i]-self.dCaAP_delta_t)/self.tau_B))
            self.I_dCaAP[j,i] = self.w_dCaAP * self.max_dCaAp_amp * (self.A_dCaAP[j,i]-self.B_dCaAP[j,i])

            
###################################################################################################

        def check_thresholds(self):
            """TODO"""
            for i in range(self.size[1]):
                for j in range(self.size[0]):
                    if self.ref_time[j, i] == 0:
                          if self.mem_prime[j, i] >= self.thr_dCaAP :
                                self.thr_mem_v[j,i] =  self.mem_prime[j, i]
                                self.pla[j, i] = 1
                                self.ref_time[j, i] = int(self.ref_dCaAP / simulation_timestep)
                                self.pla_on[j, i] = 1
                                self.spike_step_counter[j, i] = 0
                                self.dCaAP(j,i)
                                self._current[j, i] = 0
#                                 print("ref",self.ref_time[j, i])
                                
                    else: 
                        self.ref_time[j, i] -= 1
                        self.pla_on[j, i] = 0
                        self.spike_step_counter[j, i] += simulation_timestep
                        if self.ref_time[j, i] == 0:
                            self.A_dCaAP[j, i] = self.A_init
                            self.B_dCaAP[j, i] = self.B_init
                            self.I_dCaAP[j, i] = 0
                            self.pla[j, i] = 0

                        else:
                            if abs(self.A_dCaAP[j,i]-self.B_dCaAP[j,i] ) >= 0.0001:
                                self.I_dCaAP[j,i] /= (self.A_dCaAP[j,i]-self.B_dCaAP[j,i])
                                self.A_dCaAP[j,i] = 1/(1+np.exp(-(self.spike_step_counter[j,i])/self.tau_A))
                                self.B_dCaAP[j,i] = 1/(1+np.exp(-(self.spike_step_counter[j,i]-self.dCaAP_delta_t)/self.tau_B))
                                self.I_dCaAP[j,i] *= (self.A_dCaAP[j,i]-self.B_dCaAP[j,i])

                            if self.mem_prime[j,i] <= self.thr_dCaAP:
#                                 if self.pla[j, i] != 0:
#                                     print("dCaAP",j, i,self.ref_time[j, i])
                                self.pla[j, i] = 0
                                
                                
                
                            if self.mem_prime[j,i] >= self.thr_dCaAP and self.pla[j, i] == 1:
#                             if self.ref_time[j, i] > 0:
                                self._current[j, i] = 0
                                


            
            


        def check_thresholds2(self):
            """TODO"""
            for i in range(self.size[1]):
                for j in range(self.size[0]):
#                     if self.mem[j, i] >= self.v_thr:
                    if self.mem[j, i] >= self.thr_dCaAP:
                        print('spike_no_STDP')
                        if self.pla[j, i] == 0:
                            self.pla_on[j, i] = 1
                        else:
                            self.pla_on[j, i] = 0
                        self.pla[j, i] = -self.mem[j, i]
                    else:
                        self.pla[j, i] = 0
                        self.pla_on[j, i] = 0
