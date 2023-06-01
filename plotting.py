import matplotlib.pyplot as plt
import pandas as pd

results = pd.read_csv('results/result.csv')


def plot_results_for_graph_type(graph_type):
    graph_type_results = results.loc[results['graph_name'] == graph_type]
    graph_type_method_results = graph_type_results.loc[results['method'] == 'planar']
    graph_type_sat_results = graph_type_results.loc[results['method'] == 'sat']
    graph_type_sat_formula_results = graph_type_results.loc[results['method'] == 'sat_formula']
    graph_type_sat_solving_results = graph_type_results.loc[results['method'] == 'sat_solving']

    a = 0.2

    plt.title("Benchmark")
    plt.xlabel("Graph size (nodes)")
    plt.ylabel("Time taken (seconds)")
    plt.plot(graph_type_method_results['nodes'], graph_type_method_results['execution_time'], label=graph_type)
    plt.plot(graph_type_sat_results['nodes'], graph_type_sat_results['execution_time'], label="sat")
    plt.plot(graph_type_sat_formula_results['nodes'],
             graph_type_sat_formula_results['execution_time'],
             label="sat_formula",
             alpha=a)
    plt.plot(graph_type_sat_solving_results['nodes'],
             graph_type_sat_solving_results['execution_time'],
             label="sat solving",
             alpha=a)
    plt.plot(graph_type_sat_results['nodes'],
             graph_type_sat_results['execution_time']
             - graph_type_sat_solving_results['execution_time'].values
             - graph_type_sat_formula_results['execution_time'].values,
             label="sat evaluation",
             alpha=a)
    plt.legend(loc="upper left")
    plt.show()


plot_results_for_graph_type('planar')
