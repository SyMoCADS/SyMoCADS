from mmtb.experiments import get_selected_experiments
import mmtb
import mmtb.evaluation
import mmtb.evaluation.detection
import mmtb.evaluation.filters
import mmtb.evaluation.synchronization

import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams["font.family"] = "Arial"
matplotlib.rcParams["font.size"] = 15

##################
# !!! Notes !!!  # 
##############################################################################################################################
# - The parameters used in the 'Parameters' section are the default parameter settings used in the paper.                    #
# - You may need to use the native zoom tool in the Matplotlib window toolbar to zoom in; especially for longer experiments. #
##############################################################################################################################

##############
# Parameters #
##############

# Transmission Detection Parameters #
n_training = 50
false_alarm_prob = 10**-12


# Synchronization Parameters #
search_radius = 0.05


# Detection Parameters #
n_pilots = 130
n_window = 50 
n_coherence = 1
skip_n_symbols = 40


if __name__ == "__main__":


    # Get experiment data (3 options):
    experiment_data = get_selected_experiments() # Opens up the window for experiment selection
    #experiment_data = get_selected_experiments(select_files=['(2024-08-22) NMSED_5s_wEX_RT_6cm']) # Direct experiment data acces without selection window
    #experiment_data = get_selected_experiments(use_prev_selected_files=True) # Uses previously selected experiments; if no previously selected exist for the current file exist, will raise error.


    # Loops thorugh all selected experiment data
    for experiment in experiment_data:

        ##############
        # Evaluation #
        ##############

        # Blind filter values for given experiment parameters
        filter_vals = mmtb.evaluation.filters.blind_diff_filter(t_sample=experiment.spec_settings.t_sample,
                                                           t_symbol=experiment.trans_param.t_symbol,
                                                           t_irradiation=experiment.trans_param.t_irradiation)
        

        # Smoothed filter values for thee given experiment parameters
        # filter_vals = mmtb.evaluation.filters.smoothed_diff_filter(t_sample=experiment.spec_settings.t_sample,
        #                                                       t_symbol=experiment.trans_param.t_symbol,
        #                                                       t_irradiation=experiment.trans_param.t_irradiation,
        #                                                       dis_tx_rx=experiment.dis_tx_rx)


        # Instantiation of the transmission start detection class with specified parameters
        transmission_start_detection = mmtb.evaluation.synchronization.TransmissonStartDetection(training_data_length=n_training,
                                                                                                 false_alarm_probaility=false_alarm_prob)
        

        # Instantiates the synchronization class with specified parameters and associated data class for later analysis of the synchronization process.
        synchronization_data = mmtb.SynchronizationData()
        synchronization = mmtb.evaluation.synchronization.DifferentialCorrelationSynchronization(t_sample=experiment.spec_settings.t_sample,
                                                                                     t_symbol=experiment.trans_param.t_symbol,
                                                                                     filter_vals=filter_vals,
                                                                                     search_radius=search_radius,
                                                                                     n_symbols=experiment.trans_param.n_symbols,
                                                                                     sync_data=synchronization_data)
        

        # Instantiates the detection class with specified parameters and associated data class for later analysis of the detection process.
        detection_data = mmtb.DetectionData()
        detection = mmtb.evaluation.detection.ThresholdDetection(pilot_symbol_string=experiment.trans_param.total_symbol_string[:n_pilots+skip_n_symbols],
                                                                 symbol_map=experiment.trans_param.symbol_map,
                                                                 n_window=n_window,
                                                                 n_coherence=n_coherence,
                                                                 detec_data=detection_data,
                                                                 skip_n_symbols=skip_n_symbols)
        
        # Instantiates the evaluation class in order to group synchronization and detection classes to form evaluation chains. 
        evaluation = mmtb.evaluation.Evaluation(transmission_start_detec=transmission_start_detection,
                                                sync_detec_tuples=(synchronization, detection))
        

        # Groups the relative times and fluorecence values data into a 'DataPointList' instance.
        rx_samples = mmtb.DataPointList(times=experiment.rx_data.rel_times, values=experiment.rx_data.fluorescence_vals)


        # 2 evaluation options:
        # Direcly pass all available samples into the evaluation chain ...
        evaluation(rx_samples)


        # ... or sample-by-sample 
        # for sample in rx_samples:
        #     evaluation(sample)


        # Computes the average normalized absolute synchronization error and prints the result to stdout.
        print(f"Averaged normalized absolute synchronization error: {mmtb.evaluation.calculate_avg_norm_abs_rel_sync_error(t_symbol=experiment.trans_param.t_symbol,
                                                                    sync_data=synchronization_data)}")
        

        # Computes the bit error rate using Gray mapping and prints the result to stdout.
        print(f"Bit error rate (Gray mapping): {mmtb.evaluation.calculate_bit_error_rate_gray_mapping(n_pilots=n_pilots,
                                                                    transmission_param=experiment.trans_param,
                                                                    detec_data=detection_data)}")
        

        ############
        # Plotting #
        ############

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12,6), sharex=True)


        # Plots the rx data and corresponding times as vertical lines #
        ax1.plot(experiment.rx_data.rel_times, experiment.rx_data.fluorescence_vals)
        ax1.set_xlabel("Time [s]")
        ax1.vlines(x=detection_data.detection_times, ymin=0, ymax=2, linestyles='--', color='gray', label=r"$\hat{t}_{\mathrm{S}}[k]$")

        ax1.set_ylabel(r"$r(t_n)$")
        if len(experiment.spec_settings.eval_wavelengths) == 1:
            ax1.set_title(f"Normalized Fluorescence at {experiment.spec_settings.eval_wavelengths[0]} nm")
        else:
            ax1.set_title(f"Normalized Averaged Fluorescence between {experiment.spec_settings.eval_wavelengths[0]} nm to {experiment.spec_settings.eval_wavelengths[1]} nm")
        ax1.set_ylim(0, 1.2)
        ax1.set_xlim(0, experiment.rx_data.rel_times[-1])
        ax1.grid()
        ax1.legend()
        

        # Plots the metric function and synchronization times as vertical lines #
        ax2.plot(synchronization_data.metric_coeffs.times, synchronization_data.metric_coeffs.values, color="green")
        ymin = min(synchronization_data.metric_coeffs.values)
        ymax = max(synchronization_data.metric_coeffs.values)
        ax2.vlines(x=synchronization_data.detection_metric_coeffs.times, ymin=ymin, ymax=ymax, linestyles='--', color='gray')

        ax2.set_ylabel(r"$\varphi_D(t_n)$")
        ax2.set_ylim(ymin, ymax)
        ax2.set_title("Metric Function")
        ax2.set_xlabel("Time [s]")
        ax2.grid()
        

        plt.get_current_fig_manager().set_window_title(experiment.experiment_name)
        plt.tight_layout()
        plt.show()