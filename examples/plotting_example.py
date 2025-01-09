from mmtb.experiments import get_selected_experiments

if __name__ == "__main__":

    # Get experiment data (3 options):
    experiment_data = get_selected_experiments() # Opens up the window for experiment selection
    #experiment_data = get_selected_experiments(select_files=['(2024-08-22) NMSED_5s_wEX_RT_6cm']) # Direct experiment data acces without selection window
    #experiment_data = get_selected_experiments(use_prev_selected_files=True) # Uses previously selected experiments; if no previously selected exist for the current file exist, will raise error.

    # Loops thorugh all previously selected experiment data
    for experiment in experiment_data:

        # Prints experiment's transmission parameters
        print(experiment.trans_param)

        # Prints experiment's spectrometer settings
        print(experiment.spec_settings)

        # Plots RX and TX data (matplotlib.pyplot.show() included)
        experiment.plot()