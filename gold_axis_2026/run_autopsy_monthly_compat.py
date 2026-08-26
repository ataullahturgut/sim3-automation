import sklearn.linear_model
import run_autopsy_monthly as a

def CompatLogisticRegression(*args, **kwargs):
    kwargs.pop('multi_class', None)
    return sklearn.linear_model.LogisticRegression(*args, **kwargs)

a.LogisticRegression = CompatLogisticRegression

if __name__ == '__main__':
    a.main()
