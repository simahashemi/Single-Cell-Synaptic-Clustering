# 🧠 Single-Cell-Synaptic-Clustering

This repository contains code and analysis from my Master's thesis project in computational neuroscience. The project investigates how **dendritic calcium-mediated action potentials (dCaAPs)** influence **synaptic clustering** in a simulated single cell.

---

## 🧩 Project Summary

The simulation includes:
- A **compartmental neuron** with active dendritic compartments
- A network of **point neurons** simulating the input cell assemblies

The goal was to study how **dCaAPs enhance dendritic computation** and support **input clustering** and **memory stability**, in comparison to NMDA spikes.

Key components:
- Modeling of somatic and dendritic spiking
- Simulating structural and functional plasticity and Spike-Timing Dependent Plasticity (STDP)
- Analysis of synaptic input clustering
- Comparison of different learning mechanisms

---

## 🧪 Simulation Overview

This project simulates a single-compartment neuron connected to 320 point input neurons, divided into 8 assemblies of 40 neurons each. The aim is to explore synaptic clustering under different dendritic integration mechanisms and learning protocols.

We compare two models of the compartmental neuron:
- `Gidon_mc_lif_group_current.py`: Model with dendritic calcium action potentials (dCaAPs)
- `mc_lif_group.py`: NMDA-based model

You can visualize a sample dCaAP spike and its non-monotonic response in the notebook `Gidon_dCaAP.ipynb`.

Poisson spike trains for input assemblies are generated using `poisson_pattern_group.py`.

Connections between input neurons and dendrites are set up in `layers/rewiring_connection.py`, which also implements:
- Structural plasticity  
- Functional plasticity  
- STDP (Spike-Timing-Dependent Plasticity)  
- Noise  

A schematic of these plasticity mechanisms is provided in `Synaptic_dynamics_plots.ipynb`.

---

## 🧪 Learning Protocols

### 🔹 Protocol 1: Random Inputs

This protocol tests whether a neuron can learn and retain random, disjoint input assemblies. During each learning window, one of the eight assemblies is randomly selected and activated as a Poisson group firing at 35 Hz, followed by a resting window. This cycle continues for 1000 seconds.

- Run: `Random.ipynb`
- Configuration: `config_rewiring_ex2.yaml`

### 🔹 Protocol 2: Sequential Inputs

To mimic real-world learning without catastrophic forgetting, assemblies are introduced one-by-one in eight intervals of 125 seconds. During each interval, one assembly fires at 35 Hz while the rest fire at 1 Hz.

- Run: `Sequential.ipynb`
- Configuration: `config_rewiring_ex3.yaml`

### 🔹 Protocol 3: Overlapping Inputs

Here, assemblies are no longer fully disjoint. Instead, they share overlapping neurons (25%, 50%, or 75%) to simulate shared features between concepts. Assemblies are presented in random order to evaluate learning with shared features.

- Run: `Overlapping.ipynb`
- Configuration: `config_rewiring_ex5.yaml`

### 🔹 Protocol 4: Coactive Inputs

To simulate simultaneous exposure to multiple stimuli, two or more disjoint assemblies are co-activated randomly. For example, two assemblies fire together for 300 ms, followed by a 200 ms rest, and then a new pair is selected.

- Run: `Coactive.ipynb`
- Configuration: `config_rewiring_ex4.yaml` (set the number of coactive assemblies)

---

## 🛠 Running the Simulations

For each protocol, you can choose between the dCaAP model (`Gidon_mc_lif_group_current.py`) or the NMDA model (`mc_lif_group.py`). Results will be saved in the `results/` folder.

---

## 📊 Analyzing Results

Use `stats_maker.ipynb` to analyze simulation outputs. It generates a `stats.txt` file in each result directory, summarizing the number of connections and total synaptic weights per dendritic branch.

---

## 📄 License and Attribution

This project builds on [Dendritic Rewiring](https://github.com/IGITUGraz/dendritic_rewiring)  
Copyright © 2022 IGIT, TU Graz  
Licensed under the **GNU General Public License v3.0**

All modifications are © 2025 **Sima Hashemi** and are also licensed under the GNU GPL v3.  
See the [LICENSE](./LICENSE) file for full terms.

---

## 📖 Citation

If you use this project, please cite both the original work and our modifications.

**Original work** (on which this project is based):

> Limbacher, T., & Legenstein, R. (2020).  
> *Emergence of stable synaptic clusters on dendrites through synaptic rewiring*.  
> *Frontiers in Computational Neuroscience*, 14, 57.  
> https://doi.org/10.3389/fncom.2020.00057  
> [GitHub repository](https://github.com/IGITUGraz/dendritic_rewiring)

**This project**:

> Hashemi, S., Shafiee, S., & Tetzlaff, C. (2025).  
> *Robust Input Disentanglement Through Calcium-Mediated Dendritic Potentials*.  
> Master's Thesis, Georg-August University of Göttingen.  
> [GitHub repository](https://github.com/simahashemi/Single-Cell-Synaptic-Clustering)
