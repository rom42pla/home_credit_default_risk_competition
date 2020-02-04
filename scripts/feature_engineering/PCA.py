import pandas as pd
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer

from Timer import Timer

def pca_transform(df_train, dfs_to_transform, log=False):
    if log: section_timer = Timer(log=f"computing PCA")

    if "TARGET" in df_train.columns:
        df_train, y_train = df_train.drop(columns=["TARGET"]), df_train.loc[:, "TARGET"].to_numpy().tolist()
    ys_to_transform = [None, None, None]
    for i, df_to_transform in enumerate(dfs_to_transform):
        if "TARGET" in df_to_transform.columns:
            dfs_to_transform[i], ys_to_transform[i] = df_to_transform.drop(columns=["TARGET"]), df_to_transform.loc[:, "TARGET"].to_numpy().tolist()

    std_pca = make_pipeline(Normalizer(), PCA(whiten=True)).fit(df_train)
    df_train =  pd.DataFrame(data=std_pca.transform(df_train))
    selected_components = __components_selection(df_train, y_train, correlation_threshold=0.02)

    result = []
    for i, df_to_transform in enumerate(dfs_to_transform):
        df_to_transform = std_pca.transform(df_to_transform)
        df_to_transform = pd.DataFrame(data=df_to_transform)
        df_to_transform = df_to_transform[selected_components]
        result.append(df_to_transform)

    for i, df_to_transform in enumerate(dfs_to_transform):
        if ys_to_transform[i] != None:
            result[i]["TARGET"] = ys_to_transform[i]

    if log:
        section_timer.end_timer(log=f"found {len(selected_components)} components")
    return result

def __components_selection(df, target, correlation_threshold):
    df["TARGET"] = target
    #print(df.columns)
    corr_series = pd.Series(df.corr()["TARGET"])
    columns = corr_series[abs(corr_series) > correlation_threshold].index.tolist()
    columns.remove("TARGET")
    return columns