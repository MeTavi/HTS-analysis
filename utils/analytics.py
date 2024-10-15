# function for calculating the t-test for two independent samples

def ttest(data1, data2, alpha):
    
    import math
    from math import sqrt
    from scipy.stats import t

    mean1, mean2 = data1.mean(), data2.mean()
    std1, std2 = data1.std(ddof=1), data2.std(ddof=1)
    
    n1, n2 = data1.count(), data2.count()
    se1, se2 = std1/math.sqrt(n1), std2/math.sqrt(n2)

    sed = sqrt(se1**2.0 + se2**2.0)

    t_stat = (mean1 - mean2) / sed
    
    # degrees of freedom
    df = data1.count() + data2.count() - 2
    
    # calculate the critical value
    cv = t.ppf(1.0 - alpha, df)
    
    # calculate the p-value
    p = (1.0 - t.cdf(abs(t_stat), df)) * 2.0
    
    return t_stat, df, cv, p


def ttest_interpret(t_stat, cv, p, alpha):
    if abs(t_stat) <= cv:
        print('Accept null hypothesis that the means are equal.')
    else:
        print('Reject the null hypothesis that the means are equal.')
    # interpret via p-value
    if p > alpha:
        print('Accept null hypothesis that the means are equal.')
    else:
        print('Reject the null hypothesis that the means are equal.')