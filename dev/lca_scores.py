# imports
# -------
from premise import *

#brightway
import brightway2 as bw
import bw2analyzer as ba
import bw2data as bd

#common
import pandas as pd
import numpy as np

#plotting
import matplotlib.pyplot as plt
import seaborn as sns

#to be completed
import ast


# Functions for generating lca scores of ecoinvent and premise database to plot their relative changes
# Level 3 plot dependency 
# -------------------------------------------------------------------------------------------------------------------------------

def calculate_lca_ecoinvent_scores(database, method):

    ecoinvent_scores= {}
    ecoinvent_scores['method']=method #save the method used for plotting the data
    all_activities=[x for x in database]
    
    for activity in all_activities:
        activity_LCA = bw.LCA({activity:1}, bw.Method(method).name)
        activity_LCA.lci()
        activity_LCA.lcia()
        score=activity_LCA.score

         # Create a tuple key with relevant information
        key = (activity['name'], activity['unit'], activity['location'], activity.get('reference product'))

        ecoinvent_scores[key]=score

    return ecoinvent_scores

def calculate_lca_premise_scores(premise_database, method):

    premise_scores= {}

    premise_scores['method']=method #save the method used for plotting the data

    all_activities=[x for x in premise_database]
    
    for activity in all_activities:
        activity_LCA = bw.LCA({activity:1}, bw.Method(method).name)
        activity_LCA.lci()
        activity_LCA.lcia()
        score=activity_LCA.score

         # Create a tuple key with relevant information
        key = (activity['name'], activity['unit'], activity['location'], activity.get('reference product'))

        premise_scores[key]=score

    return premise_scores


# relative_changes contains the activity names as keys and their relative changes as values

def compute_relative_change(original, transformed):
    if original == 0:
        return float('inf') if transformed != 0 else 0
    return (transformed - original) / original


def calc_relative_changes(ecoinvent_scores, premise_scores):

    # Match activities_list and calculate relative changes
    relative_changes = {}
    relative_changes['method']=ecoinvent_scores['method']

    # Track additional keys in premise_scores
    additional_premise_keys = []
    
    for key, original_score in ecoinvent_scores.items():
        if key in premise_scores: #activities only in premise_scores are according to this logic neglected.
            # Skip if original_score is a tuple due to information tuple key
            if isinstance(original_score, tuple):
                continue
            
            transformed_score = premise_scores[key]
            relative_change = compute_relative_change(original_score, transformed_score)
            relative_changes[key] = relative_change

    # Identify additional keys in premise_scores
    for key in premise_scores.keys():
        if key not in ecoinvent_scores:
            additional_premise_keys.append(key)
    
    # Print the dataframes_dict
    for key, change in relative_changes.items():
        print(f"{key}: {change}")

    if additional_premise_keys:
        print("Additional keys in premise_scores not found in ecoinvent_scores:", additional_premise_keys)
    
    return relative_changes