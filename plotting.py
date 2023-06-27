import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from tqdm import tqdm


def plot_results_for_graph_type(graph_type):
    match graph_type:
        case 'p7_c3':
            results = pd.read_csv('results/result_p7c3.csv')
        case 'planar':
            results = pd.read_csv('results/result_planar.csv')
            consistency_results = pd.read_csv('results/result_planar_consistency.csv')
        case 'locally_connected':
            results = pd.read_csv('results/result_lc.csv')
            consistency_results = pd.read_csv('results/result_lc_consistency.csv')
        case _:
            print("Type not recognised...")
            return

    graph_type_results = results.loc[results['graph_name'] == graph_type]
    graph_type_results = graph_type_results.sort_values(by=['nodes'])

    graph_edges = []
    graph_densities = []
    tqdm_rows = tqdm(list(graph_type_results.iterrows()))
    tqdm_rows.set_description(desc="Looping over rows for normal results", refresh=True)

    graph = None
    for index, row in tqdm_rows:
        if graph is not None and row['nodes'] == len(graph.nodes):
            graph_edges.append(len(graph.edges()))
            graph_densities.append(nx.density(graph))
            continue

        graph = nx.read_adjlist(f"graphs/{row['graph_path']}")
        graph_edges.append(len(graph.edges()))
        graph_densities.append(nx.density(graph))

    graph_type_results['edges'] = graph_edges
    graph_type_results['density'] = graph_densities

    if graph_type != 'p7_c3':
        graph_consistency_densities = []
        tqdm_rows = tqdm(list(consistency_results.iterrows()))
        tqdm_rows.set_description(desc="Looping over rows for consistency results", refresh=True)

        for index, row in tqdm_rows:
            graph = nx.read_adjlist(f"graphs/{row['graph_path']}")
            graph_consistency_densities.append(nx.density(graph))

        consistency_results['density'] = graph_consistency_densities

    graph_type_method_results = graph_type_results.loc[results['method'] == graph_type]
    graph_type_sat_results = graph_type_results.loc[results['method'] == 'sat']
    graph_type_sat_formula_results = graph_type_results.loc[results['method'] == 'sat_formula']
    graph_type_sat_solving_results = graph_type_results.loc[results['method'] == 'sat_solving']

    a = 0.2

    fig, axs = plt.subplots(1, 2, figsize=(20, 5))

    # fig.suptitle(f"Benchmark {graph_type}")
    axs[0].set_xlabel("Graph size (edges)")
    axs[0].set_ylabel("Time taken (seconds)")
    axs[0].ticklabel_format(useOffset=False, style='plain')
    axs[0].plot(graph_type_method_results['edges'], graph_type_method_results['execution_time'], label=graph_type)
    axs[0].plot(graph_type_sat_results['edges'], graph_type_sat_results['execution_time'], label="sat total")
    axs[0].plot(graph_type_sat_formula_results['edges'],
               graph_type_sat_formula_results['execution_time'],
               label="sat formula",
               alpha=a)
    axs[0].plot(graph_type_sat_solving_results['edges'],
               graph_type_sat_solving_results['execution_time'],
               label="sat solving",
               alpha=a)
    axs[0].legend(loc="upper left")

    axs[1].set_xlabel("Graph size (edges)")
    axs[1].set_ylabel("Time taken (seconds)")
    axs[1].ticklabel_format(useOffset=False, style='plain')
    # axs[1].plot(graph_type_method_results['edges'], graph_type_method_results['execution_time'], label=graph_type)
    # axs[1].plot(graph_type_sat_results['edges'], graph_type_sat_results['execution_time'], label="sat total")
    # axs[1].plot(graph_type_sat_formula_results['edges'],
    #             graph_type_sat_formula_results['execution_time'],
    #             label="sat formula",
    #             alpha=a)
    axs[1].plot(graph_type_sat_solving_results['edges'],
                graph_type_sat_solving_results['execution_time'],
                label="sat solving")
    axs[1].legend(loc="upper left")

    fig.show()


def make_and_concat_row(combined_results, results, row):
    print(row)
    columns=['nodes', 'csp', 'sat_formula', 'sat_solving']
    sat_rows = results.loc[results['graph_path'] == row['graph_path']]
    sat_formula = sat_rows.loc[sat_rows['method'] == 'sat_formula']['execution_time'].values[0]
    sat_solving = sat_rows.loc[sat_rows['method'] == 'sat_solving']['execution_time'].values[0]
    row = pd.Series(index=columns, data=[row['nodes'], row['execution_time'], sat_formula, sat_solving])
    return pd.concat([combined_results, row.to_frame().T], ignore_index=True)


def plot_csp():
    results_csp = pd.read_csv('results/result_csp.csv')
    results_planar = pd.read_csv('results/result_planar.csv')
    results_lc = pd.read_csv('results/result_lc.csv')
    results_p7c3 = pd.read_csv('results/result_p7c3.csv')

    columns=['nodes', 'csp', 'sat_formula', 'sat_solving']
    combined_results = pd.DataFrame(columns=columns)

    for index, row in results_csp.iterrows():
        sat_rows = None
        match row['graph_name']:
            case 'locally_connected':
                combined_results = make_and_concat_row(combined_results, results_lc, row)
            case 'planar':
                combined_results = make_and_concat_row(combined_results, results_planar, row)
            case 'p7_c3':
                combined_results = make_and_concat_row(combined_results, results_p7c3, row)

    test = 0


plot_csp()
plot_results_for_graph_type('planar')
plot_results_for_graph_type('locally_connected')
plot_results_for_graph_type('p7_c3')
