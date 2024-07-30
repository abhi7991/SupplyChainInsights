from datasets import Dataset
from ragas import evaluate
from ragas.run_config import RunConfig
from ragas.metrics import (
    context_precision,
    faithfulness,
    answer_relevancy,
    context_recall,
    answer_correctness,
    answer_similarity
)
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import time
def getEval(data):

    print("Here is the " , data)
    data.iloc[:,0] = data.iloc[:,0].astype(str)
    data.iloc[:,1] = data.iloc[:,1].astype(str)
    data.iloc[:,2] = data.iloc[:,2].apply(lambda x : eval(x))
    print(data.dtypes)
    data = data.to_dict('list')
    dataset = Dataset.from_dict(data)

    score = evaluate(dataset,metrics=[faithfulness,answer_relevancy],run_config=RunConfig(max_retries=2))
    score_df = score.to_pandas()
    score_df = pd.DataFrame(score_df)

    print("Done with evaluation")
    return score_df